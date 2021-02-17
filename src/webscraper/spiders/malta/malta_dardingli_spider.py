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


class MaltaDardingliSpider(scrapy.Spider, Normalization, UploadPhoto):
    logger.info('Launching Malta Dardingli spider...')
    name = 'Dardingli'
    start_urls = [
        'https://dardingli.com/properties.html'
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
        property_urls = response.xpath("//article/div[@class='main-column clearfix']/a[1]/@href").extract()
        for link in property_urls:
            logger.info('Going to property page...')
            yield scrapy.Request(url=link, callback=self.parse_property_content)

        """Follow the pagination"""
        next_page = response.xpath("//ul[@class='pagination']/li[@class='navigator rs']/a/@href").get()
        if next_page is not None:
            logger.info('Following pagination and going to next page...')
            yield response.follow(next_page, callback=self.parse)

    def parse_property_content(self, response, **kwargs):
        items = PropertyItem()

        property_source_website = 'https://dardingli.com/'
        property_website_country = 'Malta'
        property_link = response.url
        property_script = ''.join([
            text.get()
            for text in response.xpath('//section[@id="content"]')
        ])
        property_photos_extract = self.get_list(property_script, 'data-background="', '"')[1:]
        property_photos_check = self.check_if_exists(property_photos_extract)
        if property_photos_check is not None:
            property_photos = self.store_images(property_photos_check)
            property_photo = property_photos[0]
        else:
            property_photos = None
            property_photo = None

        property_cost_extract = self.get_text(property_script, 'id="df_field_price">', '/span>')
        property_cost_pretty = self.get_text(property_cost_extract, '<span>', '<')
        property_cost = self.check_if_exists(property_cost_pretty)
        property_cost_integer = self.get_digits(property_cost)
        property_cost_currency_pretty = self.get_no_punctuation(property_cost)
        property_cost_currency_get = self.get_letters(property_cost_currency_pretty)
        property_cost_currency = self.normalize_currency(property_cost_currency_get)
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

        property_bedrooms_extract = self.get_text(property_script, 'class="badrooms">', '</span>')
        property_bedrooms = self.check_if_exists(property_bedrooms_extract)
        property_bathrooms_extract = self.get_text(property_script, 'class="bathrooms">', '</span>')
        property_bathrooms = self.check_if_exists(property_bathrooms_extract)
        property_square_extract = self.get_text(property_script, 'class="square_feet">', ' ')
        # property_square_pretty = self.get_no_punctuation(property_square_extract)
        property_square_check = self.check_if_exists(property_square_extract)
        if property_square_check is not None and '.' in property_square_check:
            property_square = property_square_check.split('.', maxsplit=1)[0]
        else:
            property_square = property_square_check
        if property_square is None:
            property_square_alt_extract = self.get_text(property_script, 'title="Plot Area">', 'end -->')
            property_square_alt_pretty = self.get_text(property_square_alt_extract, 'tpl -->', ' ')
            property_square = self.check_if_exists(property_square_alt_pretty)
            if property_square is not None and '.' in property_square:
                property_square = property_square.split('.', maxsplit=1)[0]
        property_description_extract = self.get_text(
            property_script, 'title="Description">', 'item out value tpl end -->'
        )
        property_description_pretty = self.get_text(property_description_extract, '-->', '<!-- ')
        property_description = self.check_if_exists(property_description_pretty)
        property_advertise_type_extract = self.get_text(
            property_script, 'title="Property for">', 'item out value tpl end -->'
        )
        property_advertise_type_pretty = self.get_text(property_advertise_type_extract, '-->', '<!-- ')
        property_advertise_type_check = self.check_if_exists(property_advertise_type_pretty)
        property_advertise_type = self.normalize_advertise_type(property_advertise_type_check)
        property_renewed_extract = self.get_text(property_script, 'title="Posted">', 'item out value tpl end -->')
        property_renewed_pretty = self.get_text(property_renewed_extract, 'tpl --', '!-- ')
        property_renewed_check = self.check_if_exists(property_renewed_pretty)
        if property_renewed_check is not None:
            property_renewed_day_month = self.get_text(property_renewed_check, '>', ',')
            property_renewed_day = self.get_digits(property_renewed_day_month)
            property_renewed_month_extract = self.get_no_punctuation(property_renewed_day_month)
            property_renewed_month_get = self.get_letters(property_renewed_month_extract)
            property_renewed_month = self.normalize_month(property_renewed_month_get)
            property_renewed_year_pretty = self.get_text(property_renewed_check, ',', '<')
            property_renewed_year = self.get_no_spaces(property_renewed_year_pretty)
            property_renewed = property_renewed_day + ' ' + property_renewed_month + ' ' + property_renewed_year
        property_features_extract = self.get_text(
            property_script, 'title="Property Features"', '<!-- item out value tpl end -->'
        )
        property_features_list_extract = self.get_list(property_features_extract, '<li', '</li>')[1:]
        property_existing_features_extract = []
        for element in property_features_list_extract:
            if 'active' in element:
                property_existing_features_extract.append(element)
        property_existing_features_names = []
        for element in property_existing_features_extract:
            property_existing_feature_name = self.get_text(element, 'title="', '"')
            property_existing_features_names.append(property_existing_feature_name)
        property_features = self.check_if_exists(property_existing_features_names)
        property_address_extract = self.get_text(property_script, 'id="df_field_list_of_cities">', 'end -->')
        if property_address_extract is not None:
            proterty_address_settlement_type_extract = self.get_text(property_address_extract, 'title="', '"')
            proterty_address_settlement_type = self.get_no_spaces(proterty_address_settlement_type_extract)
            property_address_settlement = self.get_text(property_address_extract, '-->', '<!--')
            property_address = property_address_settlement + ' ' + proterty_address_settlement_type + ', Malta'
            # property_address = self.get_address(property_address_raw)
            # property_coordinates = self.get_coordinates(property_address_raw)
        # else:
        #     property_address = None
            # property_coordinates = None
        property_type_extract = self.get_text(property_script, 'type="video/mp4">', 'src=')
        property_type_pretty = self.get_text(property_type_extract, 'title="', ',')
        property_type_no_commas = self.get_no_punctuation(property_type_pretty)
        property_type_no_spaces = self.get_no_spaces(property_type_no_commas)
        property_type = self.normalize_property_type(property_type_no_spaces)
        if property_address is not None and property_type is not None:
            property_slug_combine = property_address + ', ' + property_type
        else:
            property_slug_combine = property_website_country + ', ' + property_type
        property_slug = self.get_slug(property_slug_combine)
        date_time = datetime.utcnow()
        property_agency_get = self.get_text(property_script, 'Visit Agent’s Page', '</a>')
        property_agency_name_get = self.get_text(property_agency_get, '/">', '<')
        property_agency_name_pretty = self.get_no_tags(property_agency_name_get)
        property_agency = self.check_if_exists(property_agency_name_pretty)
        property_agency_link_get = self.get_list(property_agency_get, 'href="', '"')[1:]
        if property_agency_link_get is not None:
            property_agency_link = property_agency_link_get[0]
        else:
            property_agency_link = None

        items['property_source_website'] = property_source_website
        items['property_website_country'] = property_website_country
        items['property_link'] = property_link
        items['property_address'] = property_address
        # items['property_coordinates'] = property_coordinates
        items['property_cost'] = property_cost
        items['property_cost_integer'] = property_cost_integer
        items['property_cost_currency'] = property_cost_currency
        items['property_price'] = property_price
        items['property_bedrooms'] = property_bedrooms
        items['property_bathrooms'] = property_bathrooms
        items['property_square'] = property_square
        items['property_type'] = property_type
        items['property_advertise_type'] = property_advertise_type
        items['property_description'] = property_description
        items['property_features'] = property_features
        items['property_photo'] = property_photo
        items['property_photos'] = property_photos
        items['property_renewed'] = property_renewed
        items['property_agency'] = property_agency
        items['property_agency_link'] = property_agency_link
        items['property_slug'] = property_slug
        items['date_time'] = date_time

        if property_agency_link is not None:
            logger.info('Going to agency page...')
            yield scrapy.Request(url=property_agency_link, callback=self.parse_agency_content)

        logger.info('Yielding new property item...')
        yield items

    def parse_agency_content(self, response, **kwargs):
        items = AgencyItem()
        agency_source_website = 'https://dardingli.com/'
        agency_website_country = 'Malta'
        agency_link = response.url
        agency_script = ''.join([
            text.get()
            for text in response.xpath('//aside[@class="left col-lg-3"]')
        ])
        agency_name_extract = self.get_text(agency_script, 'class="seller-info">', '<div')
        agency_name_get = self.get_text(agency_name_extract, '">', "<")
        agency_name_pretty = self.get_no_tags(agency_name_get)
        agency_name = self.check_if_exists(agency_name_pretty)
        agency_logo_extract = self.get_text(agency_script, 'alt="Agent Thumbnail"', '>')
        agency_logo_link = self.get_text(agency_logo_extract, 'srcset="', '"')
        agency_logo_check = self.check_if_exists(agency_logo_link)
        if agency_logo_check is not None:
            agency_logo_list = [agency_logo_check]
            agency_logo_store = self.store_images(agency_logo_list)
            agency_logo = agency_logo_store[0]
        else:
            agency_logo = None
        agency_overview_extract = self.get_text(agency_script, 'class="about">', '</li>')
        agency_overview = self.check_if_exists(agency_overview_extract)
        if agency_overview is not None:
            agency_overview = (
                agency_overview.replace('<br>', '\n') if '<br>' in agency_overview
                else agency_overview
            )
        agency_slug = self.get_slug(agency_name)
        date_time = datetime.utcnow()

        items['agency_source_website'] = agency_source_website
        items['agency_website_country'] = agency_website_country
        items['agency_name'] = agency_name
        items['agency_logo'] = agency_logo
        items['agency_link'] = agency_link
        items['agency_overview'] = agency_overview
        items['agency_slug'] = agency_slug
        items['date_time'] = date_time

        logger.info('Yielding new agency item...')
        yield items


class MaltaDardingliScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = MaltaDardingliSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = MaltaDardingliScraper()
    scraper.run_spiders()
