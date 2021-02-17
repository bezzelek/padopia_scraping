import os
import re
import scrapy

from html import unescape
from logging import getLogger
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.webscraper.items import PropertyItem, AgencyItem
from src.webscraper.normalization.data_normalization import Normalization
from src.webscraper.normalization.process_photo import UploadPhoto


logger = getLogger()


class GreeceGrekodomSpider(scrapy.Spider, Normalization, UploadPhoto):
    logger.info('Launching Greece Grekodom spider...')
    name = 'Greece Grekodom'
    start_urls = [
        'https://www.grekodom.com/RealtyObjects?multiType=null&multiRegion=null&type=undefined&subregion=undefined&span=undefined&distance=&sortFilter=undefined&aim=&squarefrom=&squareto=&pricefrom=&priceto=&roomF=&roomT=&yearBuilt=&floorFrom=null&floorTo=null&area=undefined&areato=&seaView=false&pool=false&parking=false&furniture=false&underConstruction=false&oldBuilding=false&communalPool=false&heat=false&lift=false&newConstruction=false&isBuildableLand=false&ds=0&ex=&multiLatLong=null&page=1'
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
        property_urls = response.xpath('//div[@class="property-listing"]/ul/li/a/@href').extract()
        for link in property_urls:
            logger.info('Going to property page...')
            next_link = 'https://www.grekodom.com' + link
            yield scrapy.Request(url=next_link, callback=self.parse_property_content, priority=200)

        """Follow the pagination"""
        number_of_pages_extract = response.xpath('//span[@class="col-md-6"]').extract()
        number_of_pages = int(self.get_text(number_of_pages_extract[0], 'in ', ' '))
        pagination_list = list(range(2, number_of_pages))
        for page in pagination_list:
            pagination_url = 'https://www.grekodom.com/RealtyObjects?multiType=null&multiRegion=null&type=undefined&subregion=undefined&span=undefined&distance=&sortFilter=undefined&aim=&squarefrom=&squareto=&pricefrom=&priceto=&roomF=&roomT=&yearBuilt=&floorFrom=null&floorTo=null&area=undefined&areato=&seaView=false&pool=false&parking=false&furniture=false&underConstruction=false&oldBuilding=false&communalPool=false&heat=false&lift=false&newConstruction=false&isBuildableLand=false&ds=0&ex=&multiLatLong=null&page='
            next_page = pagination_url + str(page)
            yield response.follow(next_page, callback=self.parse, priority=10)

    def parse_property_content(self, response, **kwargs):
        p_items = PropertyItem()

        property_source_website = 'https://www.grekodom.com/'
        property_website_country = 'Greece'
        property_link = response.url
        property_script = response.text

        latitude = self.get_text(property_script, "x = parseFloat('", "'")
        longitude = self.get_text(property_script, "y = parseFloat('", "'")
        property_coordinates = {
            'latitude': latitude,
            'longitude': longitude,
        }

        property_address_extract = self.get_text(property_script, '"name":"', '"offers"')
        property_address = self.get_text(property_address_extract, 'in ', '",')

        # property_address = self.get_address_from_coordinates(
        #     property_coordinates['latitude'], property_coordinates['longitude']
        # )
        property_cost = self.get_text(property_script, '"price":"', '"')
        property_cost_integer = self.get_digits(property_cost)
        property_cost_currency_extract = self.get_text(property_script, '"priceCurrency":"', '"')
        property_cost_currency = self.normalize_currency(property_cost_currency_extract)

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

        property_type_extract = self.get_text(property_script, '"itemOffered":"', '"')
        property_type = self.normalize_property_type(property_type_extract)
        property_advertise_type_extract = self.get_text(property_script, '"name":"', '"')
        if 'Sale' in property_advertise_type_extract:
            property_advertise_type = 'Sale'
        elif 'Rent' in property_advertise_type_extract:
            property_advertise_type = 'Rent'
        else:
            property_advertise_type = 'Other'

        extract_table = self.get_text(property_script, 'table-responsive amenities-table', '</table>')
        table_to_list = self.get_list(extract_table, '<td', '</td')
        property_square_extract = []
        for element in table_to_list:
            if 'Meters' in element:
                property_square_extract.append(element)
        if property_square_extract is not None:
            property_square_get = self.get_text(str(property_square_extract), '<strong>', '<')
            property_square_digits = self.get_digits(property_square_get)
            property_square = self.check_if_exists(property_square_digits)
        else:
            property_square = None
        property_bedrooms_extract = []
        for element in table_to_list:
            if 'rooms' in element:
                property_bedrooms_extract.append(element)
        if property_bedrooms_extract is not None:
            property_bedrooms_get = self.get_text(str(property_bedrooms_extract), '<strong>', '<')
            property_bedrooms_digits = self.get_digits(property_bedrooms_get)
            property_bedrooms = self.check_if_exists(property_bedrooms_digits)
        else:
            property_bedrooms = None

        property_bathrooms_extract = []
        for element in table_to_list:
            if 'bath' in element or 'Bath' in element:
                property_bathrooms_extract.append(element)
        if property_bathrooms_extract is not None:
            property_bathrooms_get = self.get_text(str(property_bathrooms_extract), '<strong>', '<')
            property_bathrooms_digits = self.get_digits(property_bathrooms_get)
            property_bathrooms = self.check_if_exists(property_bathrooms_digits)
        else:
            property_bathrooms = None

        property_features = []
        for element in table_to_list:
            if 'default">' in element:
                key_extract = self.get_text(element, 'default">', '<br')
                value_extract = self.get_text(element, '<strong>', '</strong>')
                key_raw = unescape(key_extract.replace('\r\n', '').replace('<span>', '').replace('</span>', ''))
                value_raw = unescape(value_extract.replace('\r\n', '').replace('<span>', '').replace('</span>', ''))
                key = self.get_no_spaces(key_raw)
                value = self.get_no_spaces(value_raw)
                if '.' in key:
                    key = key.replace('.', '')
                result = {key: value}
                property_features.append(result)
        property_description_extract = unescape(self.get_text(property_script, '"description":"', '"'))
        property_description_pretty = property_description_extract.replace('<p>', '').replace('</p>', '')
        property_description_clean = property_description_pretty.replace('<span>', '').replace('</span>', '')
        property_description_final = re.sub('<.*>', '', property_description_clean)
        if '&nbsp;' in property_description_final:
            property_description_final = property_description_final.replace('&nbsp;', '')
        property_description = self.check_if_exists(property_description_final)
        property_source_language = 'England'
        property_photos_section = self.get_text(property_script, 'royalSlider rsDefault', '</div>')
        property_photos_extract = self.get_list(property_photos_section, 'href="', '"')[1:]
        property_photos_check = self.check_if_exists(property_photos_extract)
        if property_photos_check is not None:
            property_photos = self.store_images(property_photos_extract)
            property_photo = property_photos[0]
        else:
            property_photos = None
            property_photo = None

        property_agency_extract = self.get_text(property_script, 'id="nameHeading1">', '</h5>')
        property_agency = self.check_if_exists(self.get_text(property_agency_extract, '<span>', '</span>'))

        property_slug = self.get_slug(property_address)
        property_renewed = datetime.now().strftime('%d %B %Y')
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
        p_items['property_description'] = property_description
        p_items['property_features'] = property_features
        p_items['property_photo'] = property_photo
        p_items['property_photos'] = property_photos
        p_items['property_coordinates'] = property_coordinates
        p_items['property_renewed'] = property_renewed
        p_items['property_agency'] = property_agency
        p_items['property_slug'] = property_slug
        p_items['date_time'] = date_time

        if property_agency is not None:
            a_items = AgencyItem()
            agency_source_website = 'https://www.grekodom.com/'
            agency_website_country = 'Greece'
            agency_name = property_agency

            agency_logo_extract = self.get_text(property_script, 'agent-image', 'alt')
            agency_logo_url = self.check_if_exists(self.get_text(agency_logo_extract, 'src="', '"'))
            if agency_logo_url is not None and 'http' in agency_logo_url:
                agency_logo_list = [agency_logo_url]
                agency_logo_store = self.store_images(agency_logo_list)
                agency_logo = agency_logo_store[0]
            else:
                agency_logo = None
            agency_phone_extract = self.get_text(property_script, 'contact-info', '</ul>')
            agency_phone_list = self.get_list(agency_phone_extract, '<li>', '</li>')[1:]
            agency_phone = agency_phone_list[0]
            agency_slug = self.get_slug(agency_name)
            date_time = datetime.utcnow()

            a_items['agency_source_website'] = agency_source_website
            a_items['agency_website_country'] = agency_website_country
            a_items['agency_name'] = agency_name
            a_items['agency_logo'] = agency_logo
            a_items['agency_phone'] = agency_phone
            a_items['agency_slug'] = agency_slug
            a_items['date_time'] = date_time

            yield a_items

        yield p_items


class GreeceGrekodomScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = GreeceGrekodomSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = GreeceGrekodomScraper()
    scraper.run_spiders()
