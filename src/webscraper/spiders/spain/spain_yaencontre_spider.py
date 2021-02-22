import os
import scrapy

from logging import getLogger
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.webscraper.items import PropertyItem, AgencyItem
from src.webscraper.normalization.data_normalization import Normalization
from src.webscraper.normalization.process_photo import UploadPhoto


logger = getLogger()


class SpainYaencontreSpider(scrapy.Spider, Normalization, UploadPhoto):
    logger.info('Spain Yaencontre spider...')
    name = 'Spain Yaencontre'
    start_urls = [
        'https://www.yaencontre.com/'
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 400, 403, 404, 408],
        'RETRY_TIMES': 5,
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
        region_urls_extract = response.xpath(
            '//div[@class="react-tabs__tab-panel active"]/div[@class="boxLinksList "]/div[@class="nearCity"]/a/@href'
        ).extract()

        region_sale_flat_urls = []
        for link in region_urls_extract:
            logger.info('Going to region page...')
            url = 'https://www.yaencontre.com' + link
            region_sale_flat_urls.append(url)

        region_rent_flat_urls = []
        for link in region_sale_flat_urls:
            url = link.replace('venta', 'alquiler')
            region_rent_flat_urls.append(url)

        region_sale_house_urls = []
        for link in region_sale_flat_urls:
            url = link.replace('pisos', 'casas')
            region_sale_house_urls.append(url)

        region_rent_house_urls = []
        for link in region_rent_flat_urls:
            url = link.replace('pisos', 'casas')
            region_rent_house_urls.append(url)

        region_ursl_sale = region_sale_flat_urls + region_sale_house_urls
        region_ursl_rent = region_rent_flat_urls + region_rent_house_urls

        region_urls_all = region_ursl_sale + region_ursl_rent
        for link in region_urls_all:
            yield scrapy.Request(url=link, callback=self.parse_region)

    def parse_region(self, response, **kwargs):
        logger.info('Starting to scrap regions...')
        property_urls = response.xpath('//h2[@class="title d-ellipsis"]/a/@href').extract()
        for link in property_urls:
            logger.info('Going to property page...')
            url = 'https://www.yaencontre.com' + link
            yield scrapy.Request(url=url, callback=self.parse_property_content)

        """Follow the pagination"""
        next_page_extract = self.get_text(response.text, '{\\"rel\\":\\"next\\",\\"href\\":\\"', '\\"},')
        next_page = self.check_if_exists(next_page_extract)
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_property_content(self, response, **kwargs):
        p_items = PropertyItem()

        property_source_website = 'https://www.yaencontre.com/'
        property_website_country = 'Spain'

        property_link = response.url
        property_script = self.get_text(response.text, 'window.__INITIAL_STATE__ = JSON.parse', 'relateds')

        """Address and coordinates"""
        property_address_extract = self.get_text(
            response.text, 'class="mb-md address icon-placeholder-1 pointer"><span>', '</span>'
        )
        property_address = property_address_extract + ', ' + property_website_country
        property_coordinates_extract = self.get_text(property_script, 'operation', 'images')
        property_longitude = str(self.get_text(property_coordinates_extract, '"lon\\":', '},'))
        property_latitude = str(self.get_text(property_coordinates_extract, '"lat\\":', ','))
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

        """Cost"""
        property_cost_integer = self.get_text(property_script, '"price\\":', ',')
        property_cost_currency = '€'
        property_cost = property_cost_integer + ' ' + property_cost_currency

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

        """Basic info"""
        property_bedrooms_extract = self.get_text(property_script, '"rooms\\":', ',')
        property_bedrooms = self.check_if_exists(property_bedrooms_extract)

        property_bathrooms_extract = self.get_text(property_script, 'bathrooms\\":', ',')
        property_bathrooms = self.check_if_exists(property_bathrooms_extract)

        property_square_extract = self.get_text(property_script, 'area\\":', ',')
        property_square = self.check_if_exists(property_square_extract)

        property_type_extract = self.get_text(property_script, 'family\\":{\\"value\\":\\"', '\\",')
        property_type = self.normalize_property_type(property_type_extract)

        property_advertise_type_extract = self.get_text(property_script, 'operation\\":{\\"value\\":\\"', '\\",')
        property_advertise_type = self.normalize_advertise_type(property_advertise_type_extract)

        """Description"""
        property_source_language = 'Spain'
        property_description_source = self.get_text(response.text, '<div class="raw-format">', '</div>')

        """Photos"""
        property_photos_extract = self.get_text(property_script, 'images\\":[', '],')
        property_photos_pretty = self.get_list(property_photos_extract, '{\\"slug\\":\\"', '\\"}')[1:]
        property_photos_check = bool(property_photos_pretty)
        if property_photos_check:
            property_photos_prefix_extract = self.get_list(response.text, 'img src="', '"')[1:]
            property_photos_prefix = []
            for item in property_photos_prefix_extract:
                if property_photos_pretty[0] in item:
                    property_photos_prefix.append(item)
            photo_url_prefix = property_photos_prefix[0].replace(property_photos_pretty[0], '')
            property_photos_list = []
            for item in property_photos_pretty:
                image_link = photo_url_prefix + item
                property_photos_list.append(image_link)
            """Store photos"""
            property_photos = self.store_images(property_photos_list)
            property_photo = property_photos[0]
        else:
            property_photos = None
            property_photo = None

        """Agency"""
        agency_info = self.get_text(property_script, 'owner', 'operation')
        property_agency = self.get_text(agency_info, 'name\\":\\"', '\\",')
        property_agency_link_extract = self.check_if_exists(self.get_text(agency_info, 'url\\":\\"', '\\",'))
        if property_agency_link_extract is not None:
            property_agency_link = 'https://www.yaencontre.com' + property_agency_link_extract
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

        agency_check = self.check_if_exists(property_agency)
        if agency_check is not None:
            a_items = AgencyItem()

            agency_source_website = 'https://www.yaencontre.com/'
            agency_website_country = 'Spain'

            """Basic info"""
            agency_link = property_agency_link
            agency_name = property_agency
            agency_phone_one = self.get_text(agency_info, 'virtualPhoneNumber\\":\\"', '\\",')
            agency_phone_two = self.get_text(agency_info, 'whatsapp\\":\\"', '\\"},')
            agency_phone = [agency_phone_one, agency_phone_two]

            """Logo"""
            agency_logo_extract = self.get_text(agency_info, 'logo\\":{\\"slug\\":\\"', '\\"},')
            agency_logo_check = self.check_if_exists(agency_logo_extract)

            if agency_logo_check is not None:
                agency_logo_url = 'https://media.yaencontre.com/img/-/' + agency_logo_check
                agency_logo_list = [agency_logo_url]
                agency_logo_store = self.store_images(agency_logo_list)
                agency_logo = agency_logo_store[0]
            else:
                agency_logo = None

            """Technical"""
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


class SpainYaencontreScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = SpainYaencontreSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = SpainYaencontreScraper()
    scraper.run_spiders()
