import os
import json
import scrapy
import requests

from logging import getLogger
from datetime import datetime
from operator import itemgetter

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.webscraper.items import PropertyItem, AgencyItem
from src.webscraper.normalization.data_normalization import Normalization
from src.webscraper.normalization.process_photo import UploadPhoto


logger = getLogger()


class FranceImmobilierSpider(scrapy.Spider, Normalization, UploadPhoto):
    logger.info('Launching France Immobilier spider...')
    name = 'France Immobilier'
    start_urls = [
        'https://immobilier.lefigaro.fr/sitemap_index.xml'
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
        body_extract = response.text
        sitemap_extract = self.get_list(body_extract, '<loc>', '</loc>')[1:]

        sitemap_records = []
        for element in sitemap_extract:
            if 'annonce' in element:
                sitemap_records.append(element)

        recent_announce = []
        for element in sitemap_records:
            link = element
            try:
                number = int(self.get_text(element, 'annonce-', '.xml'))
                item = {
                    'link': link,
                    'number': number,
                }
                recent_announce.append(item)
            except:
                pass

        new_announce = []
        for element in sitemap_records:
            if 'new' in element:
                link = element
                number = self.get_text(element, 'new-', '.xml')
                item = {
                    'link': link,
                    'number': number,
                }
                new_announce.append(item)

        max_recent_item = max(recent_announce, key=itemgetter('number'))
        max_recent = max_recent_item['link']
        max_new_item = max(new_announce, key=itemgetter('number'))
        max_new = max_new_item['link']

        links = [max_recent, max_new]

        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_sitemap, priority=10)

    def parse_sitemap(self, response, **kwargs):
        body_extract = response.text
        sitemap_extract = self.get_list(body_extract, '<loc>', '</loc>')[1:]
        for link in sitemap_extract:
            yield scrapy.Request(url=link, callback=self.parse_property_content, priority=200)

    def parse_property_content(self, response, **kwargs):
        p_items = PropertyItem()

        property_source_website = 'https://immobilier.lefigaro.fr/'
        property_website_country = 'France'
        property_link = response.url
        property_script = response.text

        """Cost"""
        property_cost = self.get_text(property_script, 'data-detail-price-normalized="', '"')
        property_cost_integer = self.get_digits(property_cost)
        property_cost_currency_extract = self.get_text(property_script, '"priceCurrency": "', '"')
        property_cost_currency = self.normalize_currency(property_cost_currency_extract)

        """Basic"""
        property_features_extract = self.get_text(property_script, 'list-features">', '</ul>')
        property_features_list = self.get_list(property_features_extract, '<li>', '</li>')

        property_bedrooms_extract = []
        for element in property_features_list:
            if 'chambres' in element or 'chambre' in element:
                property_bedrooms_extract.append(element)
        property_bedrooms_check = self.check_if_exists(property_bedrooms_extract)
        if property_bedrooms_check is not None:
            property_bedrooms = self.get_digits(str(property_bedrooms_extract))
        else:
            property_bedrooms = None

        property_bathrooms_extract = []
        for element in property_features_list:
            if 'salles de bain' in element:
                property_bathrooms_extract.append(element)
        property_bathrooms_check = self.check_if_exists(property_bathrooms_extract)
        if property_bathrooms_check is not None:
            property_bathrooms = self.get_digits(str(property_bathrooms_extract))
        else:
            property_bathrooms = None

        property_square_extract = self.get_text(property_script, 'data-detail-area="', '"')
        if '.' in property_square_extract:
            property_square_pretty = self.get_shorter(property_square_extract, '.')
            property_square = self.get_digits(property_square_pretty)

        """Advertise"""
        property_advertise_type_extract = self.get_text(property_script, "'transaction' : '", "'")
        property_advertise_type = self.normalize_advertise_type(property_advertise_type_extract)
        property_type_extract = self.get_text(property_script, 'data-detail-estate-type="', '"')
        property_type = self.normalize_property_type(property_type_extract)

        """Description"""
        property_source_language = 'France'
        property_description_source = self.get_text(property_script, 'data-description="', '"')

        """Address"""
        latitude = self.get_text(property_script, 'data-classified-latitude="', '"')
        longitude = self.get_text(property_script, 'data-classified-longitude="', '"')
        property_coordinates = {
            'latitude': latitude,
            'longitude': longitude,
        }

        property_code = self.get_digits(property_link)
        rest_link = 'https://immobilier.lefigaro.fr/rest/classifieds/' + property_code
        rest_request = requests.get(rest_link)
        rest_response = rest_request.text
        data = json.loads(rest_response)

        # district = self.get_no_spaces(data['location']['localInformation'])
        city = data['location']['cityLabel']
        # department = data['location']['departmentLabel']
        country = data['location']['countryLabel']
        lim = ', '
        property_address = self.check_if_exists(city + lim + country)

        """Photos"""
        property_photos_extract = self.get_list(property_script, 'class="item js-img-popup">', 'class="image-link')[1:]
        property_photos_links = []
        for element in property_photos_extract:
            photo_link = self.get_text(element, '<a href="', '"')
            property_photos_links.append(photo_link)
        property_photos_check = self.check_if_exists(property_photos_links)
        if property_photos_check is not None:
            property_photos = self.store_images(property_photos_links)
            property_photo = property_photos[0]
        else:
            property_photos = None
            property_photo = None

        """Agency"""
        property_agency_extract = self.get_text(property_script, 'data-client-name="', '"')
        property_agency = self.check_if_exists(property_agency_extract)
        property_agency_link_extracrt = self.get_list(property_script, 'exit-link"', 'data-agency')[1:]
        property_agency_link_check = self.check_if_exists(property_agency_link_extracrt)
        if property_agency_link_check is not None:
            property_agency_link = (
                    'https://immobilier.lefigaro.fr' + self.get_text(property_agency_link_extracrt[0], 'href="', '"')
            )
        else:
            property_agency_link = None

        """Technical"""
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
        p_items['property_renewed'] = property_renewed
        p_items['property_agency'] = property_agency
        p_items['property_agency_link'] = property_agency_link
        p_items['property_slug'] = property_slug
        p_items['date_time'] = date_time

        if property_agency is not None:
            a_items = AgencyItem()

            agency_source_website = 'https://immobilier.lefigaro.fr/'
            agency_website_country = 'France'

            """Basic"""
            agency_name = property_agency
            agency_link = property_agency_link
            agency_info = self.get_text(property_script, 'agencyInformation', '</a>')

            """Logo"""
            agency_logo_extract = self.get_list(agency_info, 'src="', '"')[1:]
            try:
                agency_logo_check = self.check_if_exists(agency_logo_extract[0])
                if agency_logo_check is not None:
                    agency_logo_list = [agency_logo_check]
                    agency_logo_store = self.store_images(agency_logo_list)
                    agency_logo = agency_logo_store[0]
            except:
                agency_logo = None

            """Contacts"""
            agency_phone_link = 'https://immobilier.lefigaro.fr/rest/classifieds/' + property_code + '/phone'
            agency_phone_request = requests.get(agency_phone_link)
            agency_phone_response = agency_phone_request.text
            agency_phone_extract = self.get_text(agency_phone_response, '":"', '"')
            agency_phone = self.check_if_exists(agency_phone_extract)

            agency_website_extract = self.get_list(agency_info, 'href="', '"')[1:]
            try:
                agency_website = agency_website_extract[0]
            except:
                agency_website = None

            """Technical"""
            agency_slug = self.get_slug(agency_name)
            date_time = datetime.utcnow()

            a_items['agency_source_website'] = agency_source_website
            a_items['agency_website_country'] = agency_website_country
            a_items['agency_link'] = agency_link
            a_items['agency_website'] = agency_website
            a_items['agency_name'] = agency_name
            a_items['agency_logo'] = agency_logo
            a_items['agency_phone'] = agency_phone
            a_items['agency_slug'] = agency_slug
            a_items['date_time'] = date_time

            yield a_items

        yield p_items


class FranceImmobilierScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = FranceImmobilierSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = FranceImmobilierScraper()
    scraper.run_spiders()
