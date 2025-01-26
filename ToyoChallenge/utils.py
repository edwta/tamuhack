import requests

# Cache to store fetched image URLs
image_cache = {}

def fetch_car_image(make, model):
    """Fetch an image URL for a car using Google Custom Search API."""
    api_key = "AIzaSyBk5LhPKttY1f3doAsWarXNapIEhkEKWYQ"  # Replace with your API Key
    cx = "e38b58afc9c4844ef"        # Replace with your Custom Search Engine ID

    # Add site restriction for Toyota
    query = f"{make} {model} site:toyota.com"

    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={cx}&key={api_key}&searchType=image"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Return the first image link if available
        return data['items'][0]['link'] if 'items' in data else None
    except Exception as e:
        print(f"Error fetching image for {make} {model}: {e}")
        return None

def fetch_car_image_with_cache(make, model):
    """Fetch an image URL with caching."""
    key = f"{make}_{model}"  # Use make and model as the cache key
    if key in image_cache:
        return image_cache[key]  # Return cached URL if available

    image_url = fetch_car_image(make, model)
    if image_url:
        image_cache[key] = image_url  # Cache the fetched URL
    return image_url