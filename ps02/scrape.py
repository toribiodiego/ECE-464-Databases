import os
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import Base, City, Category

BASE_URL = "https://www.ubereats.com"

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# Database connection
engine = create_engine('sqlite:///ubereats.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


class CityManager:
    def __init__(self, session):
        self.session = session
        self.location_url = BASE_URL + "/location"

    def get_Cities(self):
        response = requests.get(self.location_url, headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')

        for link in soup.findAll('a', href=True):
            if '/city/' in link['href']:
                city_name = link.text.strip()
                city_subdirectory = link['href'].split('/')[-1]  # Extracts the last part as the subdirectory

                # Assuming state abbreviations are correctly part of the URL for cities
                state = city_subdirectory.split('-')[-1].upper()  # Extracts state abbreviation from subdirectory

                if not self.session.query(City).filter_by(subdirectory=city_subdirectory).first():
                    city = City(name=city_name, state=state, subdirectory=city_subdirectory)
                    self.session.add(city)
                    print(f"Added city: {city_name} with subdirectory: {city_subdirectory} and state: {state}")

        self.session.commit()
        print("City list updated successfully.")


class CategoryManager:
    def __init__(self, session):
        self.session = session
        self.categories_url = "https://www.ubereats.com/category/new-york-city"

    def get_master_category_list(self):
        try:
            response = requests.get(self.categories_url, headers=HEADERS)
            if response.status_code != 200:
                print("Failed to fetch categories: HTTP Status Code", response.status_code)
                return

            soup = BeautifulSoup(response.content, 'html.parser')

            # Use 'data-test' attribute to find category links
            category_links = soup.findAll('a', attrs={'data-test': True})
            for link in category_links:
                category_name = link['data-test'].strip()
                # Extract only the last subdirectory from the category URL
                category_subdirectory = link['href'].rstrip('/').split('/')[-1]

                # Ensure the category is not duplicated
                if not self.session.query(Category).filter_by(name=category_name,
                                                              subdirectory=category_subdirectory).first():
                    category = Category(name=category_name, subdirectory=category_subdirectory)
                    self.session.add(category)
                    print(f"Added category: {category_name} with subdirectory: {category_subdirectory}")

            self.session.commit()
            print("Master category list updated successfully.")
        except Exception as e:
            self.session.rollback()
            print(f"An error occurred while updating the master category list: {e}")


def main():
    session = Session()
    city_manager = CityManager(session)
    city_manager.get_Cities()  # Fetch and store cities

    category_manager = CategoryManager(session)
    category_manager.get_master_category_list()  # Fetch and store categories


if __name__ == "__main__":
    main()
