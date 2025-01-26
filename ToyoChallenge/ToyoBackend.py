import os
import json
from flask import Flask, render_template, jsonify, request
from elasticsearch_client import get_elasticsearch_client
from utils import fetch_car_image
from utils import fetch_car_image_with_cache
from utils import ensure_url_scheme
from toyotaDataExtractor2 import getCarLinks
from toyotaDataExtractor2 import getCarData
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
es = get_elasticsearch_client()  # Connect to Elasticsearch (default: localhost:9200)

# INDEX VEHICLE DATA TO ELASTICSEARCH
def index_vehicle_data():
    """
    Index vehicle data into Elasticsearch only if the index is empty.
    """
    file_path = os.path.join(os.path.dirname(__file__), 'data', 'vehicles.json')

    # Check if the index already exists
    if es.indices.exists(index="vehicles"):
        print("Elasticsearch index 'vehicles' already exists. Skipping indexing.")
        return

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            for idx, vehicle in enumerate(data):
                es.index(index="vehicles", id=idx, document=vehicle)
        print("Vehicle data indexed successfully.")
    except FileNotFoundError:
        print("Error: JSON file not found.")
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")

def construct_car_url(model):
    """
    Constructs a URL to search for the car on the Autotrader website.
    Args:
        model (str): The model name of the car.
    Returns:
        str: The constructed URL.
    """
    base_url = "https://www.autotrader.com/cars-for-sale/all-cars/toyota/"
    # Format the model name for the query
    formatted_model = model.replace(" ", "+").lower()  # Replace spaces with '+' and convert to lowercase
    search_url = f"{base_url}?query={formatted_model}"
    return search_url

def fetch_price_dynamically(model):
    """
    Fetches the price of a car dynamically by constructing the search URL
    and scraping the first result.
    Args:
        model (str): The model name of the car.
    Returns:
        str: The price of the car.
    """
    try:
        # Construct the URL
        car_url = construct_car_url(model)

        # Fetch the page
        page = requests.get(car_url, timeout=10)
        soup = BeautifulSoup(page.text, 'html.parser')

        # Extract the price from the first listing
        price_element = soup.find(attrs={'data-cmp': 'firstPrice'})
        if price_element:
            return price_element.text.strip()

        return "Price not available"
    except Exception as e:
        print(f"Error fetching price for {model}: {e}")
        return "Error fetching price"


# ROUTES
@app.route('/')
@app.route('/home')
def home():
    return render_template('about.html')


@app.route('/index', methods=['GET'])
def index():
    try:
        response = es.search(
            index="vehicles",
            query={"match": {"make": "Toyota"}},
            size=25  # Fetch a limited number of Toyota cars
        )
        cars = [hit['_source'] for hit in response['hits']['hits']]
        for car in cars:
            car['year'] = car.get('year', 'N/A')
            car['fueltype'] = car.get('fueltype', 'Unknown')
            car['drive'] = car.get('drive', 'Unknown')
            car['fuelcost08'] = car.get('fuelcost08', 'N/A')
            car['image_url'] = fetch_car_image_with_cache(car['make'], car['model']) or "/static/images/toyota_generic.jpg"
        return render_template('index.html', cars=cars)
    except Exception as e:
        print(f"Error fetching Toyota cars: {e}")
        return render_template('index.html', cars=[], error="Unable to fetch cars.")




@app.route('/search', methods=['GET'])
def search():
    # Render the search input form if no query parameters are provided
    if not any(request.args.values()):
        return render_template('search.html')  # Render the search form page

    # Collect query parameters
    make = request.args.get('make', '').lower()
    model = request.args.get('model', '').lower()
    price_min = request.args.get('price_min', type=int)
    price_max = request.args.get('price_max', type=int)
    fueltype = request.args.get('fueltype', '').lower()
    year = request.args.get('year', type=int)
    sort_field = request.args.get('sort', 'price')  # Default to price sort
    sort_order = request.args.get('order', 'asc').lower()  # Default ascending order
    page = int(request.args.get('page', 1))  # Default to page 1
    page_size = int(request.args.get('size', 9))  # Default page size
    start = (page - 1) * page_size  # Calculate the starting index

    # Elasticsearch base query
    query = {"bool": {"must": [], "filter": []}}

    if make:
        query["bool"]["must"].append({"match": {"make": make}})
    if model:
        query["bool"]["must"].append({"match": {"model": model}})
    if year:
        query["bool"]["filter"].append({"term": {"year": str(year)}})
    if fueltype:
        query["bool"]["must"].append({"match": {"fueltype": fueltype}})

    # Elasticsearch search with sorting and pagination
    try:
        response = es.search(
            index="vehicles",
            query=query,
            from_=start,
            size=page_size,
            sort=[{"year.keyword": {"order": sort_order}}]  # Sorting by year or other valid fields
        )

        filtered_vehicles = [
            {
                **hit['_source'],
                "id": hit['_id']
            }
            for hit in response['hits']['hits']
        ]

        # Dynamically fetch and filter prices
        # Dynamically fetch and filter prices
        prices = []
        for vehicle in filtered_vehicles:
            try:
                # Image search
                vehicle['image_url'] = ensure_url_scheme(
                    fetch_car_image_with_cache(vehicle['make'], vehicle['model'])
                ) or "static/images/toyota_generic.jpg"

                # Fetch the price using the scraper (assumes model is sufficient)
                vehicle_price = fetch_price_dynamically(vehicle['model'])
                
                # Ensure price is an integer
                vehicle['price'] = int(vehicle_price.replace("$", "").replace(",", "").strip()) if vehicle_price else None
                
                # Add to price list for filtering and range calculation
                if vehicle['price'] is not None:
                    prices.append(vehicle['price'])
            except ValueError:
                # Handle any conversion issues (e.g., invalid price format)
                vehicle['price'] = None

        # Apply price filtering locally
        if price_min is not None or price_max is not None:
            filtered_vehicles = [
                vehicle for vehicle in filtered_vehicles
                if vehicle.get('price') is not None and
                (price_min is None or vehicle['price'] >= price_min) and
                (price_max is None or vehicle['price'] <= price_max)
            ]

        # Sort locally by price if specified
        if sort_field == 'price':
            filtered_vehicles = sorted(
                filtered_vehicles,
                key=lambda x: x.get('price', float('inf')),
                reverse=(sort_order == 'desc')
            )

        # Calculate min and max price for UI
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        # Paginate results
        total_results = len(filtered_vehicles)
        paginated_vehicles = filtered_vehicles[start:start + page_size]

        # Render results
        return render_template(
            'search_results.html',
            vehicles=paginated_vehicles,
            total_results=total_results,
            page=page,
            page_size=page_size,
            sort=sort_field,
            order=sort_order,
            min_price=min_price,
            max_price=max_price
        )

    except Exception as e:
        print(f"Error during search: {e}")
        return render_template('search_results.html', error=str(e))



@app.route('/vehicle/<id>', methods=['GET'])
def vehicle_details(id):
    try:
        # Fetch the vehicle details from Elasticsearch by document ID
        response = es.get(index="vehicles", id=id)
        vehicle = response['_source']

        # Render the details page
        return render_template('vehicle_details.html', vehicle=vehicle)
    except Exception as e:
        print(f"Error fetching vehicle details for ID {id}: {e}")
        return render_template('vehicle_details.html', error="Vehicle not found"), 404


@app.route('/compare')
def compare():
    ids = request.args.get('ids', '').split(',')
    
    if not ids or ids == ['']:
        return render_template('compare.html', error="No cars selected for comparison.")
    
    try:
        query = {
            "query": {
                "terms": {
                    "id": ids
                }
            }
        }
        response = es.search(index="vehicles", body=query)
        vehicles = [hit['_source'] for hit in response['hits']['hits']]
        return render_template('compare.html', vehicles=vehicles)
    except Exception as e:
        return render_template('compare.html', error=f"Error fetching vehicles: {e}")



if __name__ == '__main__':
    # Index data to Elasticsearch before starting the app
    index_vehicle_data()
    app.run(debug=True)

