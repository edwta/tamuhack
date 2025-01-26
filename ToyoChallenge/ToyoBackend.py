import os
import json
from flask import Flask, render_template, jsonify, request
from elasticsearch_client import get_elasticsearch_client
from utils import fetch_car_image
from utils import fetch_car_image_with_cache
from utils import ensure_url_scheme

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
    price = request.args.get('price', type=int)
    year = request.args.get('year', type=int)
    price_min = request.args.get('price_min', type=int)
    price_max = request.args.get('price_max', type=int)
    fueltype = request.args.get('fueltype', '').lower()

    # Sorting and validation
    sort_field = request.args.get('sort', 'fuelcost08')  # Default sort field
    sort_order = request.args.get('order', 'asc').lower()  # Default to ascending order
    valid_sort_fields = ['year', 'fuelcost08']  # Valid fields for sorting

    if sort_field not in valid_sort_fields:
        sort_field = 'fuelcost08'  # Default to fuel cost if the field is invalid

    # Ensure proper mapping for sortable fields like "year"
    if sort_field == 'year':
        sort_field += ".keyword"

    if sort_order not in ['asc', 'desc']:
        sort_order = 'asc'  # Default order if invalid

    # Pagination
    page = int(request.args.get('page', 1))  # Default to page 1
    page_size = int(request.args.get('size', 9))  # Default page size
    start = (page - 1) * page_size  # Calculate the starting index

    # Elasticsearch query with filters
    query = {"bool": {"must": [], "filter": []}}

    if make:
        query["bool"]["must"].append({"match": {"make": make}})
    if model:
        query["bool"]["must"].append({"match": {"model": model}})
    if price:
        query["bool"]["filter"].append({"range": {"fuelcost08": {"lte": price}}})
    if year:
        query["bool"]["filter"].append({"term": {"year": str(year)}})
    if price_min is not None:
        query["bool"]["filter"].append({"range": {"price": {"gte": price_min}}})
    if price_max is not None:
        query["bool"]["filter"].append({"range": {"price": {"lte": price_max}}})
    if fueltype:
        query["bool"]["must"].append({"match": {"fueltype": fueltype}})

    print("Constructed Query:", query)  # Debugging log

    # Elasticsearch search with sorting and pagination
    try:
        response = es.search(
            index="vehicles",
            query=query,
            from_=start,
            size=page_size,
            sort=[{sort_field: {"order": sort_order}}]
        )
        filtered_vehicles = [
            {
                **hit['_source'],
                "id": hit['_id'] 
            }
            for hit in response['hits']['hits']
        ]
        total_results = response['hits']['total']['value']  # Total number of results

        # Add images to vehicles
        for vehicle in filtered_vehicles:
            vehicle['image_url'] = ensure_url_scheme(fetch_car_image_with_cache(vehicle['make'], vehicle['model'])) or "static/images/toyota_generic.jpg"
            print(f"Vehicle: {vehicle['make']} {vehicle['model']} - Image URL: {vehicle['image_url']}")  # Debugging

        # Render results in a template
        return render_template(
            'search_results.html',
            vehicles=filtered_vehicles,
            total_results=total_results,
            page=page,
            page_size=page_size,
            sort=sort_field,
            order=sort_order
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

