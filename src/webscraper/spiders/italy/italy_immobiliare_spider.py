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
from src.webscraper.normalization.geolocate import Geolocation

logger = getLogger()


class ItalyImmobiliareSpider(scrapy.Spider, Normalization, UploadPhoto, Geolocation):
    logger.info('Launching Italy Immobiliare spider...')
    name = 'Italy'
    start_urls = [
        'https://www.immobiliare.it/'
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
        self.geolocation_client = self.start_geolocation_client()

    def parse(self, response, **kwargs):
        logger.info('Starting to scrap...')
        region_urls_extract = response.xpath(
            "//li[@class='nd-listMeta__item nd-listMeta__item--meta']/a/@href"
        ).extract()

        region_sale_urls = []
        for url in region_urls_extract:
            link = url[:-7]
            region_sale_urls.append(link)

        region_rent_urls = []
        for url in region_sale_urls:
            link = url.replace('vendita-case', 'affitto-case')
            region_rent_urls.append(link)

        region_urls = region_sale_urls + region_rent_urls
        for link in region_urls:
            yield scrapy.Request(url=link, callback=self.parse_search_page, priority=1)

    def parse_search_page(self, response, **kwargs):
        """Getting links of property pages in particular search page"""
        property_urls = response.xpath("//div[@class='listing-item_body--content']/p/a/@href").extract()
        for link in property_urls:
            logger.info('Going to property page...')
            yield scrapy.Request(url=link, callback=self.parse_property_content, priority=400)

        """Follow the pagination"""
        next_page = response.xpath("//ul[@class='pull-right pagination']/li[1]/a/@href").get()
        if next_page is not None:
            logger.info('Following pagination and going to next page...')
            yield response.follow(next_page, callback=self.parse, priority=15)

    def parse_property_content(self, response, **kwargs):
        p_items = PropertyItem()

        property_source_website = 'https://www.immobiliare.it/'
        property_website_country = 'Italy'
        property_link = response.url

        script = response.xpath('//script[@id="js-hydration"]/text()').get()
        data = json.loads(script)

        property_cost = data['listing']['properties'][0]['price']['formattedPriceTop'][0]
        property_cost_integer = str(data['listing']['properties'][0]['price']['price'])
        property_cost_currency = self.normalize_currency(data['listing']['properties'][0]['price']['currency'])
        property_square_extract = data['listing']['properties'][0]['surfaceValue']
        if property_square_extract is not None:
            property_square_shorter = self.get_shorter(property_square_extract, ' ')
            property_square = self.get_digits(property_square_shorter)
        else:
            property_square = None
        property_source_language = 'Italy'
        property_description_source = data['listing']['properties'][0]['description']
        property_type = self.normalize_property_type(data['listing']['properties'][0]['typology']['name'])

        try:
            property_bedrooms = str(data['trovakasa']['locMin'])
        except:
            property_bedrooms = None
        try:
            property_bathrooms = str(data['trovakasa']['bagni'])
        except:
            property_bathrooms = None
        property_advertise_type = self.normalize_advertise_type(data['listing']['contract']['type'])
        try:
            property_agency = data['listing']['advertiser']['agency']['displayName']
            property_agency_link = data['listing']['advertiser']['agency']['agencyUrl']
        except:
            property_agency = None
            property_agency_link = None

        property_photos_extract = data['listing']['properties'][0]['multimedia']['photos']
        if property_photos_extract is not None:
            property_photos_links = []
            for element in property_photos_extract:
                photo = element['urls']['large']
                property_photos_links.append(photo)
            property_photos = self.store_images(property_photos_links)
            property_photo = property_photos[0]
        else:
            property_photos = None
            property_photo = None
        latitude = str(data['listing']['properties'][0]['location']['latitude'])
        longitude = str(data['listing']['properties'][0]['location']['longitude'])
        if latitude is not None and longitude is not None:
            property_coordinates = {
                'latitude': latitude,
                'longitude': longitude,
            }
        else:
            property_coordinates = None

        property_address = self.get_address_from_coordinates(
            property_coordinates['latitude'], property_coordinates['longitude']
        )

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

            agency_source_website = 'https://www.immobiliare.it/'
            agency_website_country = 'Italy'
            agency_link = data['listing']['advertiser']['agency']['agencyUrl']
            agency_name = data['listing']['advertiser']['agency']['displayName']
            agency_phone = data['listing']['advertiser']['agency']['phones'][0]['value']
            agency_slug = self.get_slug(agency_name)
            try:
                agency_logo_check = data['listing']['advertiser']['agency']['imageUrl']
            except:
                agency_logo_check = None
            if agency_logo_check is not None:
                agency_logo_list = [agency_logo_check]
                agency_logo_store = self.store_images(agency_logo_list)
                agency_logo = agency_logo_store[0]
            else:
                agency_logo = None
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


class ItalyImmobiliareScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = ItalyImmobiliareSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = ItalyImmobiliareScraper()
    scraper.run_spiders()
