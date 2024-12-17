import requests #get data from website
from bs4 import BeautifulSoup #webscraping
import pandas as pd 
import re 
import os 
import numpy as np

class Waitrose:
    def __init__(self, url):
        self.url = url
        
    def webscraping(self):
        # Improved error handling for requests
        try:
            # Use session for better performance
            session = requests.Session()
            html = session.get(self.url)
            html.raise_for_status()  # Raise error for bad status codes
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

        # Use explicit parser
        soup = BeautifulSoup(html.text, 'html.parser')

        # More robust class name finding
        def find_class_containing(soup, prefix):
            for tag in soup.find_all(True, class_=True):
                if prefix in tag.get('class')[0]:
                    return tag.get('class')[0]
            return None

        title_class = find_class_containing(soup, 'name___')
        price_class = find_class_containing(soup, 'prices___')

        if not title_class or not price_class:
            print("Could not find dynamic classes")
            return None

        # Scraping with error handling
        title, price_temp, link = [], [], []

        # Find all product pods
        product_pods = soup.find_all("article", {"data-testid": "product-pod"})
        
        for pod in product_pods:
            try:
                # Title
                title_elem = pod.find("span", {"class": title_class})
                if title_elem:
                    title.append(title_elem.text.strip())

                # Price
                price_elem = pod.find("div", {"class": price_class})
                if price_elem:
                    price_temp.append(price_elem.text.strip())

                # Link
                link_elem = pod.find("a")
                if link_elem and link_elem.has_attr('href'):
                    full_link = f"https://www.waitrose.com{link_elem['href']}"
                    link.append(full_link)

            except Exception as e:
                print(f"Error processing pod: {e}")
                continue

        # Create DataFrame
        df = pd.DataFrame({
            'title': title,
            'price_temp': price_temp,
            'link': link
        })

        # Price cleaning helper function
        def clean_price(price_str):
            if not isinstance(price_str, str):
                return None
            
            # Remove £ or convert p to decimal
            if price_str.startswith('£'):
                return float(price_str[1:])
            elif price_str.endswith('p'):
                return float(price_str[:-1]) / 100
            return None

        # Splitting and cleaning data
        try:
            # Split price information
            df[['price', 'price_per_unit', 'unit']] = df['price_temp'].str.split('/', expand=True)

            # Clean prices
            df['price'] = df['price'].apply(clean_price)
            df['price_per_unit'] = df['price_per_unit'].apply(clean_price)

            # Clean units
            df['unit'] = df['unit'].str.replace('ml', 'ltr')

            # Final cleanup
            df = df.dropna().drop_duplicates().reset_index(drop=True)

        except Exception as e:
            print(f"Data cleaning error: {e}")
            return None

        return df