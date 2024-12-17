import waitrose_scraper
from waitrose_scraper import Waitrose

waitrosescraper = Waitrose('https://www.waitrose.com/ecom/shop/search?&searchTerm=milk')
response = waitrosescraper.webscraping()
print(response)