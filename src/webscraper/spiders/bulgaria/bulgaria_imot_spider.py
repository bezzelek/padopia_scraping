import os
import gzip

import scrapy

from io import BytesIO
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


class BulgariaImotSpider(scrapy.Spider, Normalization, UploadPhoto, Currency):
    logger.info('Launching Bulgaria spider...')
    name = 'Imot'
    start_urls = [
        'https://www.imot.bg/sitemap/index.xml'
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
        response_text = response.text
        extract_sitemap_links = self.get_list(response_text, '<loc>', '</loc>')[3:]
        sitemap_info = []
        for link in extract_sitemap_links:
            year = ''.join(link.split('_sitemap')[1].split('-')[0])
            week = ''.join(link.split('-')[1].split('.')[0])
            item = {
                'link': link,
                'year': int(year),
                'week': int(week),
            }
            sitemap_info.append(item)
        max_year_item = max(sitemap_info, key=itemgetter('year'))
        max_year = max_year_item['year']
        current_year_elements = []
        for element in sitemap_info:
            if max_year == element['year']:
                current_year_elements.append(element)
        max_week_element = max(current_year_elements, key=itemgetter('week'))
        path_to_doc = max_week_element['link']
        yield scrapy.Request(url=path_to_doc, callback=self.parse_sitemap)

    def parse_sitemap(self, response, **kwargs):
        read_sitemap = gzip.GzipFile(fileobj=BytesIO(response.body)).read().decode()
        property_links = self.get_list(read_sitemap, '<loc>', '</loc>')[1:]
        for link in property_links:
            yield scrapy.Request(url=link, callback=self.parse_property_content)

    def parse_property_content(self, response, **kwargs):
        p_items = PropertyItem()
        a_items = AgencyItem()

        property_source_website = 'https://www.imot.bg/'
        property_website_country = 'Bulgaria'
        property_link = response.url
        property_script = ''.join([
            text.get()
            for text in response.xpath('//script/text()')
            if 'var w2g =' in text.get()
        ])
        property_document_extract = response.text

        """Property advertise type"""
        property_advertise_type_extract = int(self.get_text(property_script, "'AdvertPubtype': ['", "']"))
        if property_advertise_type_extract > 0:
            property_advertise_type = self.normalize_advertise_type(property_advertise_type_extract)
        else:
            property_advertise_type = None

        """Property type"""
        property_type_extract = self.get_text(property_script, "'AdvertTypeImot': ['", "']")
        property_type_check = self.check_if_exists(property_type_extract)
        if property_type_check is not None:
            property_type = self.normalize_property_type(property_type_extract)
        else:
            property_type = None

        """Property address"""
        property_address_original = self.get_text(property_document_extract, "Местоположение: <b>", "</b>")
        property_address = self.check_if_exists(property_address_original)
        # if property_address_check is not None:
        #     property_address = self.get_address(property_address_original)
        #     property_coordinates = self.get_coordinates(property_address_original)
        # else:
        #     property_address = None
        #     property_coordinates = None

        """Property cost"""
        property_cost_extract = self.get_text(property_document_extract, '<strong style="color: #900">', "</strong>")
        if 'При запитване' in property_cost_extract:
            property_cost = None
            property_cost_integer = None
            property_cost_currency = None

            property_price = {
                'eur': {
                    'amount': None,
                    'currency_iso': None,
                    'currency_symbol': None,
                },
                'source': {
                    'amount': None,
                    'currency_iso': None,
                    'currency_symbol': None,
                },
                'price_last_update': datetime.utcnow(),
            }

        else:
            property_cost = property_cost_extract
            property_cost_integer = self.get_digits(property_cost)
            property_cost_currency_get = self.get_letters(property_cost)
            property_cost_currency = self.normalize_currency(property_cost_currency_get)

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

        """Bedrooms"""
        property_bedrooms_extract = self.get_text(
            property_document_extract, '<strong style="font-size:18px;">', '</strong>'
        )
        property_bedrooms_number = self.get_digits(property_bedrooms_extract)
        property_bedrooms_check = property_bedrooms_number.isdigit()
        if property_bedrooms_check:
            property_bedrooms = property_bedrooms_number
        else:
            property_bedrooms = None

        """Property square"""
        property_square_extract = self.get_text(property_document_extract, 'Квадратура:', " ")
        property_square_integer = self.get_digits(property_square_extract)
        property_square = self.check_if_exists(property_square_integer)

        """Property description"""
        property_source_language = 'Bulgaria'
        property_description_extract = self.get_text(property_document_extract, 'id="description_div">', "</div>")
        property_description_check = self.check_if_exists(property_description_extract)
        if property_description_check is not None:
            property_description_source = (
                property_description_extract.replace('<br>', '\n') if '<br>' in property_description_extract
                else property_description_extract
            )
        else:
            property_description_source = None

        """Property renewed"""
        property_renewed_extract = self.get_text(property_document_extract, 'margin:11px 0 3px 0">', "</div>")
        property_renewed_year = self.get_text(property_renewed_extract, ', ', ' ')
        property_renewed_day_month = self.get_text(property_renewed_extract, ' на ', ', ')
        property_renewed_month_extract = self.get_letters(property_renewed_day_month).strip()
        property_renewed_month = self.normalize_month(property_renewed_month_extract)
        property_renewed_day = self.get_digits(property_renewed_day_month)
        property_renewed = property_renewed_day + ' ' + property_renewed_month + ' ' + property_renewed_year

        """Property photos"""
        property_photos_source = ''.join([
            text.get()
            for text in response.xpath('//script/text()')
            if 'var picts=new' in text.get()
        ])
        property_photos_extract = self.get_list(property_photos_source, "'//", "'")[1:]
        property_photos_check = self.check_if_exists(property_photos_extract)
        if property_photos_check is not None:
            property_photos_list = []
            for item in property_photos_check:
                link = 'https://' + item
                property_photos_list.append(link)
            property_photos = self.store_images(property_photos_list)
            property_photo = property_photos[0]
        else:
            property_photos = None
            property_photo = None

        """Property agent"""
        property_agent_original = self.get_text(property_document_extract, '<b>Брокер: ', "</b>")
        property_agent = self.check_if_exists(property_agent_original)
        property_agent_photo_extract = ''.join(
            element.split('"')[0]
            for element in property_document_extract.split('<img src="..')[1:]
            if 'brokerspicts' in element
        )
        property_agent_photo_exists = self.check_if_exists(property_agent_photo_extract)
        if property_agent_photo_exists is not None:
            property_agent_photo_link = 'https://www.imot.bg' + property_agent_photo_extract
            property_agent_photo = self.store_images(property_agent_photo_link)
        else:
            property_agent_photo = None
        property_agency_original = self.get_text(property_document_extract, '<b>Агенция: ', "<br></b>")
        property_agency = self.check_if_exists(property_agency_original)

        """Property slug and our update time"""
        property_slug = self.get_slug(property_address)
        date_time = datetime.utcnow()

        p_items['property_source_website'] = property_source_website
        p_items['property_website_country'] = property_website_country
        p_items['property_link'] = property_link
        p_items['property_address'] = property_address
        # p_items['property_coordinates'] = property_coordinates
        p_items['property_cost'] = property_cost
        p_items['property_cost_integer'] = property_cost_integer
        p_items['property_cost_currency'] = property_cost_currency
        p_items['property_price'] = property_price
        p_items['property_bedrooms'] = property_bedrooms
        p_items['property_square'] = property_square
        p_items['property_type'] = property_type
        p_items['property_advertise_type'] = property_advertise_type
        p_items['property_source_language'] = property_source_language
        p_items['property_description_source'] = property_description_source
        p_items['property_photo'] = property_photo
        p_items['property_photos'] = property_photos
        p_items['property_renewed'] = property_renewed
        p_items['property_agent'] = property_agent
        p_items['property_agent_photo'] = property_agent_photo
        p_items['property_agency'] = property_agency
        p_items['property_slug'] = property_slug
        p_items['date_time'] = date_time

        if property_agency is not None:

            agency_logo_extract = self.get_text(property_document_extract, 'class="logo"><img src="..', '"')
            agency_logo_check = self.check_if_exists(agency_logo_extract)
            if agency_logo_check is not None:
                agency_logo_link = 'https://www.imot.bg' + agency_logo_check
                agency_logo_list = [agency_logo_link]
                agency_logo_store = self.store_images(agency_logo_list)
                agency_logo = agency_logo_store[0]
            else:
                agency_logo = None
            agency_link_extract = self.get_text(property_document_extract, 'rel="nofollow">', '</a>')
            agency_link = self.check_if_exists(agency_link_extract)
            agency_phone_extract = self.get_text(property_document_extract, ':-4px;">', '</span>')
            agency_phone = self.check_if_exists(agency_phone_extract)
            agency_slug_extract = self.get_slug(property_agency)
            agency_slug = self.check_if_exists(agency_slug_extract)

            a_items['agency_source_website'] = property_source_website
            a_items['agency_website_country'] = property_website_country
            a_items['agency_name'] = property_agency
            a_items['agency_logo'] = agency_logo
            a_items['agency_link'] = agency_link
            a_items['agency_phone'] = agency_phone
            a_items['agency_slug'] = agency_slug
            a_items['date_time'] = date_time

            yield a_items

        logger.info('Yielding new property item...')
        yield p_items


class BulgariaImotScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = BulgariaImotSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = BulgariaImotScraper()
    scraper.run_spiders()
