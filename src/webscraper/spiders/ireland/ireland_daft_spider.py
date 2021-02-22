import os
import json

import scrapy

from logging import getLogger
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from src.webscraper.items import PropertyItem, AgencyItem
from src.webscraper.normalization.data_normalization import Normalization
from src.webscraper.normalization.process_photo import UploadPhoto


logger = getLogger()


class IrelandDaftSpider(scrapy.Spider, Normalization, UploadPhoto):
    logger.info('Launching Ireland spider...')
    name = 'Daft'
    start_urls = [
        'https://www.daft.ie/property-for-sale/ireland',
        'https://www.daft.ie/property-for-rent/ireland',
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage_client = self.start_client_storage()

    def parse(self, response, **kwargs):
        logger.info('Starting to scrap...')
        home_page = 'https://www.daft.ie'
        script = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        data = json.loads(script)
        data_extract = data['props']['pageProps']['listings']
        final_data = []
        for element in data_extract:
            extracted_data = element['listing']
            final_data.append(extracted_data)
        property_list = []
        for element in final_data:
            if 'numBathrooms' in element:
                property_list.append(element)

        for element in property_list:
            next_page = home_page + element['seoFriendlyPath']
            logger.info('Going to property page...')
            yield response.follow(next_page, callback=self.parse_property_content)

        script_pagination = response.text
        next_page_extract = self.get_list(script_pagination, '<a hre', '</a>')
        for item in next_page_extract:
            if 'Next page' in item:
                next_page_get = self.get_text(item, 'f="', '" ')
                next_page = home_page + next_page_get
        if next_page is not None:
            logger.info('Following pagination and going to nex page...')
            yield response.follow(next_page, callback=self.parse)

    def parse_property_content(self, response, **kwargs):
        logger.info('Scraping property page...')
        p_items = PropertyItem()

        property_source_website = 'https://www.daft.ie/'
        property_website_country = 'Ireland'
        property_link = response.url
        script = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        data = json.loads(script)
        final_data = data['props']['pageProps']['listing']

        property_address_extract = final_data['title']
        property_address = self.check_if_exists(property_address_extract)
        property_bedrooms_extract = final_data['numBedrooms']
        property_bedrooms = self.get_digits(property_bedrooms_extract)
        property_bathrooms_extract = final_data['numBathrooms']
        property_bathrooms = self.get_digits(property_bathrooms_extract)
        property_type_extract = final_data['propertyType']
        property_type = self.normalize_property_type(property_type_extract)
        property_source_language = 'England'
        property_description_extract = final_data['description']
        property_description = self.check_if_exists(property_description_extract)
        try:
            property_facilities_extract = final_data['facilities']
            property_facilities = self.check_if_exists(property_facilities_extract)
        except:
            property_facilities = None
        try:
            property_features_extract = final_data['features']
            property_features = self.check_if_exists(property_features_extract)
        except:
            property_features = None

        """Photos extract"""
        try:
            property_photos_extract = final_data['media']['images']
        except:
            property_photos_extract = None
        if property_photos_extract is not None:
            property_photos_get = []
            for element in property_photos_extract:
                link = next(iter(element.values()))
                if 'http' in link:
                    property_photos_get.append(link)
                else:
                    element.pop('caption', None)
                    link = next(iter(element.values()))
                    property_photos_get.append(link)
        """Photos save"""
        property_photo_check = self.check_if_exists(property_photos_get)
        if property_photo_check is not None:
            property_photos = self.store_images(property_photo_check)
            property_photo = property_photos[0]
        else:
            property_photos = None
            property_photo = None

        property_renewed_extract = final_data['lastUpdateDate']
        property_renewed = self.check_if_exists(property_renewed_extract)
        latitude_extract = final_data['point']['coordinates'][1]
        longitude_extract = final_data['point']['coordinates'][0]
        property_coordinates_extract = {
            'latitude': latitude_extract,
            'longitude': longitude_extract,
        }

        longitude = self.check_if_exists(longitude_extract)
        latitude = self.check_if_exists(latitude_extract)
        if longitude is not None and latitude is not None:
            property_geo = {
                'type': 'Point',
                'coordinates': [
                    float(longitude),
                    float(latitude)
                ]
            }
        else:
            property_geo = None

        property_coordinates = self.check_if_exists(property_coordinates_extract)
        try:
            property_square_extract = final_data['floorArea']['value']
            property_square = self.check_if_exists(property_square_extract)
        except:
            property_square = None
        try:
            if 'Sale' in final_data['sellingType']:
                property_advertise_type_extract = 'Sale'
        except:
            if 'Rent' in final_data['category']:
                property_advertise_type_extract = 'Rent'
        property_advertise_type = self.normalize_advertise_type(property_advertise_type_extract)

        property_cost_extract = final_data['price']
        property_cost = self.check_if_exists(property_cost_extract)
        property_cost_integer = self.get_digits(property_cost_extract)
        if property_advertise_type == "Sale":
            property_cost_currency_extract = self.get_no_punctuation(property_cost_extract)
            property_cost_currency_pretty = self.get_letters(property_cost_currency_extract)
            property_cost_currency = property_cost_currency_pretty[-1]
        else:
            property_cost_currency_extract = self.get_no_punctuation(property_cost_extract)
            property_cost_currency_pretty = self.get_letters(property_cost_currency_extract)
            property_cost_currency = property_cost_currency_pretty[:1]

        property_price = {
            'eur': {
                'amount': int(property_cost_integer),
                'currency_iso': 'EUR',
                'currency_symbol': '€',
            },
            'source': {
                'amount': int(property_cost_integer),
                'currency_iso': 'EUR',
                'currency_symbol': '€',
            },
            'price_last_update': datetime.utcnow(),
        }

        try:
            property_agency_extract = final_data['seller']['branch']
            property_agency = self.check_if_exists(property_agency_extract)
        except:
            property_agency = None
        property_slug = self.get_slug(property_address)
        date_time = datetime.utcnow()

        p_items['property_source_website'] = property_source_website
        p_items['property_website_country'] = property_website_country
        p_items['property_link'] = property_link
        p_items['property_address'] = property_address
        p_items['property_cost'] = property_cost
        p_items['property_cost_integer'] = property_cost_integer
        p_items['property_cost_currency'] = property_cost_currency
        p_items['property_price'] = property_price
        p_items['property_square'] = property_square
        p_items['property_bedrooms'] = property_bedrooms
        p_items['property_bathrooms'] = property_bathrooms
        p_items['property_type'] = property_type
        p_items['property_advertise_type'] = property_advertise_type
        p_items['property_source_language'] = property_source_language
        p_items['property_description'] = property_description
        p_items['property_facilities'] = property_facilities
        p_items['property_features'] = property_features
        p_items['property_coordinates'] = property_coordinates
        p_items['property_geo'] = property_geo
        p_items['property_photo'] = property_photo
        p_items['property_photos'] = property_photos
        p_items['property_renewed'] = property_renewed
        p_items['property_agency'] = property_agency
        p_items['property_slug'] = property_slug
        p_items['date_time'] = date_time

        """Agency"""
        try:
            agency_check = final_data['seller']['branch']
        except:
            agency_check = None
        if agency_check is not None:
            a_items = AgencyItem()
            agency_info = final_data['seller']
            agency_source_website = 'https://www.daft.ie/'
            agency_website_country = 'Ireland'
            agency_name = agency_info['branch']
            try:
                agency_logo_check = self.check_if_exists(agency_info['squareLogo'])
            except:
                agency_logo_check = None
            if agency_logo_check is not None:
                agency_logo_list = [agency_logo_check]
                agency_logo_store = self.store_images(agency_logo_list)
                agency_logo = agency_logo_store[0]
            else:
                agency_logo = None

            try:
                agency_phone = self.check_if_exists(agency_info['phone'])
            except:
                agency_phone = None
            agency_slug = self.get_slug(
                agency_name if agency_name is not None
                else None
            )
            date_time = datetime.utcnow()

            a_items['agency_source_website'] = agency_source_website
            a_items['agency_website_country'] = agency_website_country
            a_items['agency_name'] = agency_name
            a_items['agency_logo'] = agency_logo
            a_items['agency_phone'] = agency_phone
            a_items['agency_slug'] = agency_slug
            a_items['date_time'] = date_time
            logger.info('Yielding new agency item...')
            yield a_items

        logger.info('Yielding new property item...')
        yield p_items


class IrelandDaftScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = IrelandDaftSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = IrelandDaftScraper()
    scraper.run_spiders()
