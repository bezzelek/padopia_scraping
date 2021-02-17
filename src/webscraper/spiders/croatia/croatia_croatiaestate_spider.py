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


class CroatiaCroatiaestateSpider(scrapy.Spider, Normalization, UploadPhoto):
    logger.info('Launching Croatia-Estate spider...')
    name = 'Croatia-Estate'
    start_urls = [
        'https://croatia-estate.com/properties/?',
        'https://croatia-estate.com/properties/for-rent,for-sale/?ct%5B%5D=909&ct%5B%5D=910&price_from=&price_to='
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

        property_urls = response.xpath('//div[@class="properties__info"]/a/@href').extract()

        for link in property_urls:
            logger.info('Going to property page...')
            yield scrapy.Request(url=link, callback=self.parse_property_content)

        """Follow the pagination"""
        next_page = self.get_text(response.text, '<link rel="next" href="', '" />')

        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_property_content(self, response, **kwargs):
        p_items = PropertyItem()

        property_source_website = 'https://croatia-estate.com/'
        property_website_country = 'Croatia'

        property_link = response.url
        property_script = self.get_text(response.text, '<!-- BEGIN PROPERTY DETAILS-->', '<!-- END PROPERTY DETAILS-->')

        """Address"""
        property_address_extract = self.get_text(property_script, '"property__city"', '/span>')
        property_address_city = self.get_no_spaces(self.get_text(property_address_extract, '>', '<'))
        property_address = property_address_city + ', Croatia'

        """Cost"""
        property_cost_extract = self.get_text(property_script, '"property__price"', '/span')
        property_cost = self.get_no_spaces(self.get_text(property_cost_extract, 'strong>', '</'))
        property_cost_integer = self.get_digits(property_cost)
        property_cost_currency = self.normalize_currency(property_cost[-1:])

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
        property_bedrooms_extract = self.get_text(property_script, 'title">Rooms</dd>', '/dd>')
        property_bedrooms = self.check_if_exists(self.get_text(property_bedrooms_extract, '">', '<'))

        property_bathrooms_extract = self.get_text(property_script, 'title">Bathrooms</dd>', '/dd>')
        property_bathrooms = self.check_if_exists(self.get_text(property_bathrooms_extract, '">', '<'))

        property_square_extract = self.get_text(property_script, 'title">Area (m<sup>2</sup>)</dd>', '/dd>')
        property_square = self.check_if_exists(self.get_text(property_square_extract, '">', '<'))

        property_type_extract = self.get_text(property_script, 'item">Property type:<strong> ', '</strong>')
        property_type = self.normalize_property_type(property_type_extract)

        property_advertise_type_extract = self.get_text(property_script, 'ribon">', '</div>')
        property_advertise_type = self.normalize_advertise_type(property_advertise_type_extract)

        property_features_extract = self.get_text(property_script, 'params-list--options">', '</ul>')
        property_features = self.get_list(property_features_extract, '- ', '</li>')[1:]

        """Description"""
        property_source_language = 'England'
        property_description_extract = self.get_text(property_script, 'description-wrap1">', '</div>')
        property_description = unescape(re.sub('<[^<]+?>', '', property_description_extract))

        """Photos"""
        property_photos_extract = self.get_text(property_script, 'slider--fixed" >', 'data-slick data-wrapper>')
        property_photos_check = self.check_if_exists(self.get_list(property_photos_extract, 'data-src="', '">')[1:])

        if property_photos_check is not None:
            property_photos = self.store_images(property_photos_check)
            property_photo = property_photos[0]
        else:
            property_photos = None
            property_photo = None

        """Agency"""
        property_agency_extract = self.get_text(property_script, '"worker__name fn"><a href', '/h3>')
        property_agency = self.get_text(property_agency_extract, '>', '<')
        property_agency_link = self.get_text(property_agency_extract, '="', '"')

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
        p_items['property_description'] = property_description
        p_items['property_features'] = property_features
        p_items['property_photo'] = property_photo
        p_items['property_photos'] = property_photos
        p_items['property_renewed'] = property_renewed
        p_items['property_agency'] = property_agency
        p_items['property_agency_link'] = property_agency_link
        p_items['property_slug'] = property_slug
        p_items['date_time'] = date_time

        agency_check = self.check_if_exists(property_agency)
        if agency_check is not None:
            a_items = AgencyItem()

            agency_source_website = 'https://croatia-estate.com/'
            agency_website_country = 'Croatia'

            """Basic info"""
            agency_link = property_agency_link
            agency_name = property_agency
            agency_phone = self.get_text(response.text, '"header__span">Office: ', ' ·')

            """Logo"""
            agency_logo_extract = self.get_text(property_script, 'class="photo"', 'alt=')
            agency_logo_check = self.check_if_exists(self.get_text(agency_logo_extract, 'src="', '"'))

            if agency_logo_check is not None:
                agency_logo_list = [agency_logo_check]
                agency_logo_store = self.store_images(agency_logo_list)
                agency_logo = agency_logo_store[0]
            else:
                agency_logo = None

            """Description"""
            agency_overview = self.check_if_exists(
                unescape(self.get_text(property_script, 'worker__descr">', '</div>'))
            )

            """Technical"""
            agency_slug = self.get_slug(agency_name)
            date_time = datetime.utcnow()

            a_items['agency_source_website'] = agency_source_website
            a_items['agency_website_country'] = agency_website_country
            a_items['agency_link'] = agency_link
            a_items['agency_phone'] = agency_phone
            a_items['agency_name'] = agency_name
            a_items['agency_logo'] = agency_logo
            a_items['agency_overview'] = agency_overview
            a_items['agency_slug'] = agency_slug
            a_items['date_time'] = date_time

            yield a_items

        yield p_items


class CroatiaCroatiaestateScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = CroatiaCroatiaestateSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = CroatiaCroatiaestateScraper()
    scraper.run_spiders()
