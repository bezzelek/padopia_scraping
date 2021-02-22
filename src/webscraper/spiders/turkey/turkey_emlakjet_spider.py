import os
import re
import json
import scrapy
import dateparser

from html import unescape
from logging import getLogger
from datetime import datetime
from operator import itemgetter

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.webscraper.items import PropertyItem, AgencyItem
from src.webscraper.normalization.data_normalization import Normalization
from src.webscraper.normalization.process_photo import UploadPhoto
from src.webscraper.normalization.currency_exchange import Currency


logger = getLogger()


class TurkeyEmlakjetSpider(scrapy.Spider, Normalization, UploadPhoto, Currency):
    logger.info('Launching Turkey Emlakjet spider...')
    name = 'Turkey Emlakjet'
    start_urls = [
        'https://www.emlakjet.com/sitemaps/index.xml'
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
        self.exchange_rates = self.collect_exchange_rate()

    def parse(self, response, **kwargs):
        logger.info('Starting to scrap...')
        body_extract = response.text
        sitemap_extract = self.get_list(body_extract, '<loc>', '</loc>')[1:]

        sitemap_records = []
        for element in sitemap_extract:
            if 'detail' in element:
                sitemap_records.append(element)

        sitemap_sale = []
        for element in sitemap_records:
            if 'satilik' in element:
                link = element
                number = int(self.get_text(element, 'p_', '.xml'))
                item = {
                    'link': link,
                    'number': number,
                }
                sitemap_sale.append(item)

        sitemap_rent = []
        for element in sitemap_records:
            if 'kiralik' in element:
                link = element
                number = int(self.get_text(element, 'p_', '.xml'))
                item = {
                    'link': link,
                    'number': number,
                }
                sitemap_rent.append(item)

        max_sale_item = max(sitemap_sale, key=itemgetter('number'))
        max_sale = max_sale_item['link']
        max_rent_item = max(sitemap_rent, key=itemgetter('number'))
        max_rent = max_rent_item['link']

        links = [max_sale, max_rent]

        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_sitemap, priority=10)

    def parse_sitemap(self, response, **kwargs):
        body_extract = response.text
        sitemap_extract = self.get_list(body_extract, '<loc>', '</loc>')[1:]
        for link in sitemap_extract:
            yield scrapy.Request(url=link, callback=self.parse_property_content, priority=200)

    def parse_property_content(self, response, **kwargs):
        p_items = PropertyItem()

        property_source_website = 'https://www.emlakjet.com/'
        property_website_country = 'Turkey'
        property_link = response.url

        script = self.get_text(response.text, 'id="__NEXT_DATA__"', 'script>')
        script_clean = self.get_text(script, 'json">', '</')
        data = json.loads(script_clean)
        property_data = data['props']['initialProps']['pageProps']['pageResponse']
        property_info = property_data['info']

        """Property address"""
        district = property_data['location']['district']['name']
        town = property_data['location']['town']['name']
        city = property_data['location']['city']['name']
        lim = ', '
        property_address = district + lim + town + lim + city

        property_longitude = str(property_data['location']['coordinates']['lon'])
        property_latitude = str(property_data['location']['coordinates']['lat'])
        longitude = self.check_if_exists(property_longitude)
        latitude = self.check_if_exists(property_latitude)

        if longitude is not None and latitude is not None:
            property_coordinates = {
                'latitude': latitude,
                'longitude': longitude,
            }
            property_geo = {
                'type': 'Point',
                'coordinates': [
                    float(longitude),
                    float(latitude)
                ]
            }
        else:
            property_coordinates = None
            property_geo = None

        """Property cost"""
        property_cost = str(property_data['price']['value']) + ' ' + property_data['price']['currency']
        property_cost_integer = str(property_data['price']['value'])
        property_cost_currency = self.normalize_currency(property_data['price']['currency'])

        property_cost_currency_iso = self.normalize_currency_iso(property_cost_currency)
        property_price_eur_amount = self.convert_price(
            property_cost_integer, property_cost_currency_iso, self.exchange_rates
        )

        property_price = {
            'eur': {
                'amount': int(property_price_eur_amount),
                'currency_iso': 'EUR',
                'currency_symbol': '€',
            },
            'source': {
                'amount': int(property_cost_integer),
                'currency_iso': property_cost_currency_iso,
                'currency_symbol': property_cost_currency,
            },
            'price_last_update': datetime.utcnow(),
        }

        """Property base info"""
        try:
            property_bathrooms_extract_dict = list(filter(lambda item: item['key'] == 'bath_count', property_info))[0]
            property_bathrooms_extract = property_bathrooms_extract_dict['value']
            if property_bathrooms_extract == 'Yok':
                property_bathrooms = '1'
            else:
                property_bathrooms = property_bathrooms_extract
        except:
            property_bathrooms = None

        try:
            property_bedrooms_extract_dict = list(filter(lambda item: item['key'] == 'room_count', property_info))[0]
            property_bedrooms_extract = property_bedrooms_extract_dict['value']
            property_bedrooms_digits = re.findall('([0-9]?[+]?[0-9])', property_bedrooms_extract)[0]
            property_bedrooms = str(eval(property_bedrooms_digits))
        except:
            property_bedrooms = None

        try:
            property_square_extract_dict = list(filter(lambda item: item['key'] == 'gross_square', property_info))[0]
            property_square_extract = property_square_extract_dict['value']
            property_square = self.get_no_spaces(self.get_shorter(property_square_extract, ' '))
        except:
            property_square = None

        """Advertise info"""
        property_advertise_type = self.normalize_advertise_type(property_data['tradeType']['key'])

        property_type_extract_dict = list(
            filter(lambda item: item['key'] == 'kategori_3', property_data['gtmDataLayer'])
        )[0]
        property_type_extract = property_type_extract_dict['value'][0]
        property_type = self.normalize_property_type(property_type_extract)

        """Property description"""
        property_source_language = 'Turkey'
        property_description_source_extract = property_data['description']
        property_description_source = unescape(re.sub('<[^<]+?>', '', property_description_source_extract))

        """Property photos"""
        try:
            property_photos_extract = property_data['images']
        except:
            property_photos_extract = None
            property_photos = None
            property_photo = None

        if property_photos_extract is not None:
            property_photos = self.store_images(property_photos_extract)
            property_photo = property_photos[0]
        else:
            property_photos = None
            property_photo = None

        """Agency details"""
        property_agency = property_data['owner']['account']['name']
        property_agency_link_extract = self.get_text(response.text, 'class="_2Ko6r" href="', '">')
        property_agency_link_check = self.check_if_exists(property_agency_link_extract)
        if property_agency_link_check is not None:
            url = 'https://www.emlakjet.com'
            property_agency_link = url + property_agency_link_check
        else:
            property_agency_link = None

        property_slug = self.get_slug(property_address)
        property_renewed_extract = dateparser.parse(property_data['updatedAt'][:10])
        property_renewed = property_renewed_extract.strftime('%d %B %Y')
        date_time = datetime.utcnow()

        p_items['property_source_website'] = property_source_website
        p_items['property_website_country'] = property_website_country
        p_items['property_link'] = property_link
        p_items['property_address'] = property_address
        p_items['property_cost'] = property_cost
        p_items['property_cost_integer'] = property_cost_integer
        p_items['property_cost_currency'] = property_cost_currency
        p_items['property_price'] = property_price
        p_items['property_bedrooms'] = property_bedrooms
        p_items['property_bathrooms'] = property_bathrooms
        p_items['property_square'] = property_square
        p_items['property_type'] = property_type
        p_items['property_advertise_type'] = property_advertise_type
        p_items['property_source_language'] = property_source_language
        p_items['property_description_source'] = property_description_source
        p_items['property_photo'] = property_photo
        p_items['property_photos'] = property_photos
        p_items['property_coordinates'] = property_coordinates
        p_items['property_geo'] = property_geo
        p_items['property_renewed'] = property_renewed
        p_items['property_agency'] = property_agency
        p_items['property_agency_link'] = property_agency_link
        p_items['property_slug'] = property_slug
        p_items['date_time'] = date_time

        if property_agency is not None:
            a_items = AgencyItem()
            agency_source_website = 'https://www.emlakjet.com/'
            agency_website_country = 'Turkey'

            agency_link = property_agency_link
            agency_name = property_agency

            """Agency logo"""
            try:
                agency_logo_extract = property_data['owner']['account']['logo']
                url = 'https://imaj.emlakjet.com'
                agency_logo_link = url + agency_logo_extract
                agency_logo_list = [agency_logo_link]
                agency_logo_store = self.store_images(agency_logo_list)
                agency_logo = agency_logo_store[0]
            except:
                agency_logo = None

            """Agency phone"""
            try:
                agency_phone = property_data['owner']['account']['phoneNumber']
            except:
                agency_phone = None

            agency_slug = self.get_slug(agency_name)
            date_time = datetime.utcnow()

            a_items['agency_source_website'] = agency_source_website
            a_items['agency_website_country'] = agency_website_country
            a_items['agency_link'] = agency_link
            a_items['agency_name'] = agency_name
            a_items['agency_logo'] = agency_logo
            a_items['agency_phone'] = agency_phone
            a_items['agency_slug'] = agency_slug
            a_items['date_time'] = date_time

            yield a_items

        yield p_items


class TurkeyEmlakjetScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = TurkeyEmlakjetSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = TurkeyEmlakjetScraper()
    scraper.run_spiders()
