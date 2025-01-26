import os
import json
from flask import Flask, render_template, jsonify, request
from elasticsearch_client import get_elasticsearch_client
from utils import fetch_car_image
from utils import fetch_car_image_with_cache

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
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    # Elasticsearch query to retrieve all vehicles
    try:
        response = es.search(index="vehicles", query={"match_all": {}})
        vehicles = [hit['_source'] for hit in response['hits']['hits']]
        return jsonify(vehicles), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/search', methods=['GET'])
def search():
    # Check if there are query parameters; if not, render the input form
    if not any(request.args.values()):
        return render_template('search.html')  # Render the search form page

    # Collect query parameters
    make = request.args.get('make', '').lower()
    model = request.args.get('model', '').lower()
    price = request.args.get('price', type=int)
    year = request.args.get('year', type=int)

    # Image search with Google Search API
    # image_url = fetch_car_image(make, model)
    # print(f"Fetched image URL: {image_url}")

    # Sorting
    sort_field = request.args.get('sort', 'fuelcost08')
    if sort_field == "year":  # Assuming year is the problematic field
        sort_field += ".keyword"
    sort_order = request.args.get('order', 'asc')  # Default sort order

    # Pagination
    page = int(request.args.get('page', 1))  # Default to page 1
    page_size = int(request.args.get('size', 10))  # Default page size
    # Calculate the starting index for pagination
    start = (page - 1) * page_size

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
        filtered_vehicles = [hit['_source'] for hit in response['hits']['hits']]
        total_results = response['hits']['total']['value']  # Total number of results

        # Add images to vehicles
        for vehicle in filtered_vehicles:
            vehicle['image_url'] = fetch_car_image_with_cache(vehicle['make'], vehicle['model']) or "static/images/placeholder.jpg"
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


@app.route('/vehicle/<int:id>', methods=['GET'])
def vehicle_details(id):
    try:
        response = es.get(index="vehicles", id=id)
        return render_template('vehicle_details.html', vehicle=response['_source'])
    except Exception as e:
        return "Vehicle not found", 404



if __name__ == '__main__':
    # Index data to Elasticsearch before starting the app
    index_vehicle_data()
    app.run(debug=True)

