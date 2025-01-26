import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Cache to store fetched image URLs
image_cache = {}

def ensure_url_scheme(url):
    """Ensure the URL has an http or https scheme."""
    if url and not url.startswith(('http://', 'https://')):
        return f"https://{url}"  # Default to https
    return url

def fetch_car_image(make, model):
    """Fetch an image URL for a car using Google Custom Search API."""
    api_key = os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CX")   

    # Add site restriction for Toyota
    query = f"{make} {model} site:toyota.com"

    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={cx}&key={api_key}&searchType=image&num=9"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()

        # Return the first valid image link if available
        if 'items' in data and len(data['items']) > 0:
            return data['items'][0]['link']
        
            # Validate URL is an image
            head = requests.head(image_url, allow_redirects=True)
            if 'image' in head.headers['Content-Type']:
                return image_url
            else:
                print(f"Invalid image URL: {image_url}")
                return None
        else:
            print(f"No image found for {make} {model}")
            return None
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