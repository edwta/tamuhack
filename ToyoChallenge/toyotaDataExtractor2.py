import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

# replace url later
def getCarLinks(url):
    options = Options()
    #options.add_experimental_option("detach", True)
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")  # Recommended for headless mode on Windows
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)

    time.sleep(3)

    scroll_pause_time = 0.25  # Pause time between scrolls
    scroll_step = 700  # Number of pixels to scroll at each step
    current_scroll_position = 0
    page_height = driver.execute_script("return document.body.scrollHeight")

    while current_scroll_position < page_height:
        # Scroll by a small step
        driver.execute_script(f"window.scrollTo(0, {current_scroll_position + scroll_step});")
        current_scroll_position += scroll_step
        
        # Wait for new content to load
        WebDriverWait(driver,10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.item-card-body a'))
        )
        
        # Update the page height (in case new content is loaded)
        page_height = driver.execute_script("return document.body.scrollHeight")

    car_links = driver.find_elements(By.CSS_SELECTOR, 'div.item-card-body a' )

    hrefs = [link.get_attribute('href') for link in car_links]
    driver.quit()
    return hrefs

def getCarData(url):
    """This function takes a url input from the autotrade website focusing on a specific car and returns important elements of the car in the form of a dictionary.

    Args:
        url (string): a string with the url with the car you want to get data from

    Returns:
        dictionary: a dictionary with elements of, carURL, name, price, mileage, engineType, cityMpg, highwayMpg, color, wheelDrive, and rating
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')

    data = {}
    data['carURL'] = url

    # Gets the name of the car
    data['name'] = soup.find(id='vehicle-details-heading').text


    # Gets the price of the car
    data['price'] = soup.find(attrs={'data-cmp':'firstPrice'}).text

    # Get other data
    tempData = soup.find(attrs={'data-cmp':'listColumns'})
    listOfData = tempData.find_all(class_='gap-1')
    data['mileage'] = ''
    data['engineType'] = ''
    data['cityMpg'] = ''
    data['highwayMpg'] = ''
    data['exteriorColor'] = ''
    data['interiorColor'] = ''
    data['wheelDrive'] = ''
    for allData in listOfData:
        if 'miles' in allData.text:
            data['mileage'] = allData.text
            continue
        elif 'City' in allData.text:
            mpgTotal = allData.text.replace(" City /","").replace(" Highway", "")
            data['cityMpg'], data['highwayMpg'] = mpgTotal.split()
            continue
        elif 'Exterior' in allData.text:
            data['exteriorColor']=allData.text.replace(" Exterior", "")
            continue
        elif 'Interior' in allData.text:
            data['interiorColor'] = allData.text.replace(" Interior", "")
        elif 'wheel' in allData.text:
            data['wheelDrive'] = allData.text
        elif 'Gas' in allData.text or 'Hybrid' in allData.text or 'Electric' in allData.text:
            data['engineType'] = allData.text
    # Get star rating for the car
    ratingElement = soup.find(attrs={'data-cmp':'starRating'})
    if (ratingElement == None):
        data['rating'] = ''
    else:
        data['rating'] = ratingElement.find(class_='text-bold').text
    return data


def getResults(url):
    carLinks = getCarLinks(url)
    print(carLinks)
    carData = []
    print("in get results")
    for link in carLinks:
        data = getCarData(link)
        carData.append(data)
        
    return carData
    
url = "https://www.autotrader.com/cars-for-sale/all-cars/toyota/"
print(getResults(url))