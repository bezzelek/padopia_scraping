import os
import scrapy

from html import unescape
from logging import getLogger
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from webscraper.proxies import get_proxies
from src.webscraper.items import PropertyItem, AgencyItem
from src.webscraper.normalization.process_photo import UploadPhoto
from src.webscraper.normalization.data_normalization import Normalization


logger = getLogger()


class SpainFotocasaSpider(scrapy.Spider, Normalization, UploadPhoto):
    logger.info('Launching Spain Fotocasa spider...')
    name = 'Fotocasa'
    start_urls = [
        'https://www.fotocasa.es/en/buy/homes/espana/all-zones/l',
        'https://www.fotocasa.es/en/rental/homes/espana/all-zones/l'
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS': 5,

        'RETRY_HTTP_CODES': [500, 502, 503, 504, 400, 403, 404, 408, 456],
        'ROTATING_PROXY_PAGE_RETRY_TIMES': 10000,
        'ROTATING_PROXY_LOGSTATS_INTERVAL': 15,
        'ROTATING_PROXY_BACKOFF_BASE': 300,
        'ROTATING_PROXY_BACKOFF_CAP': 900,
        'ROTATING_PROXY_LIST': get_proxies(),
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
            'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.storage_client = self.start_client_storage()

    def parse(self, response, **kwargs):
        logger.info('Starting to scrap...')
        website = 'https://www.fotocasa.es'
        script = response.text
        property_urls = self.get_list(script, '"en-GB\\":\\"', '\\"},')[2:]
        for link in property_urls:
            url = website + link
            logger.info('Going to property page...')
            yield scrapy.Request(url=url, callback=self.parse_property_content)

        """Follow the pagination"""
        next_page_extract = response.xpath(
            "//li[@class='sui-PaginationBasic-item sui-PaginationBasic-item--control']/a/@href"
        ).extract()
        next_page_check = len(next_page_extract)

        if next_page_check == 1:
            next_page = next_page_extract[0]
        elif next_page_check == 2:
            next_page = next_page_extract[1]
        else:
            next_page = None

        if next_page is not None:
            next_url = website + next_page
            logger.info('Following pagination and going to next page...')
            yield response.follow(next_url, callback=self.parse)

    def parse_property_content(self, response, **kwargs):
        items = PropertyItem()
        script = response.text

        website = 'https://www.fotocasa.es'
        property_source_website = 'https://www.fotocasa.es/en/'
        property_website_country = 'Spain'
        property_link = response.url

        base_info_extract = self.get_list(script, 're-DetailHeader-featuresItemValue', '</span></li>')
        property_bedrooms_extract = self.get_if_element_in(base_info_extract, '">', '<', 'bdrm')
        property_bedrooms = self.check_if_exists(property_bedrooms_extract)
        property_bathrooms_extract = self.get_if_element_in(base_info_extract, '">', '<', 'bathroom')
        property_bathrooms = self.check_if_exists(property_bathrooms_extract)
        property_square_extract = self.get_if_element_in(base_info_extract, '">', '<', 'sqm')
        property_square = self.check_if_exists(property_square_extract)
        property_source_language = 'Spain'
        property_description_extract = self.get_text(script, 'fc-DetailDescription">', '</p>')
        property_description_check = self.check_if_exists(property_description_extract)
        if property_description_check is not None:
            property_description_source = unescape(
                property_description_extract.replace('<br />', '\n') if '<br />' in property_description_extract
                else property_description_extract
            )
        property_cost_extract = self.get_text(script, 're-DetailHeader-price">', '<')
        property_cost = self.check_if_exists(property_cost_extract)
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

        features_info_extract = self.get_list(script, 're-DetailFeaturesList-featureLabe', 'div>')
        property_features_extract = []
        for item in features_info_extract:
            if 'DetailEnergyCertificate' in item:
                feature = self.get_text(item, 'l">', '<')
                existing_extract = self.get_text(item, 'DetailEnergyCertificate', '/')
                existing = self.get_text(existing_extract, '>', '<')
                element = {feature: existing}
                property_features_extract.append(element)
            else:
                feature = self.get_text(item, 'l">', '<')
                existing = self.get_text(item, 'Value">', '<')
                element = {feature: existing}
                property_features_extract.append(element)
        property_features_check = self.check_if_exists(property_features_extract)
        if property_features_check is not None:
            property_features = property_features_check[2:]
        else:
            property_features = None
        property_type_extract = self.get_if_element_in(features_info_extract, 'Value">', '</p>', 'Typology')
        property_type = self.normalize_property_type(property_type_extract)
        property_facilities_extract = self.get_list(script, 're-DetailExtras-listItem">', '<')
        property_facilities_check = self.check_if_exists(property_facilities_extract)
        if property_facilities_check is not None:
            property_facilities = property_facilities_check[1:]
        else:
            property_facilities = None
        property_photos_extract = self.get_list(script, 'largeSizeUrl\\":\\"', '\\"')[1:]
        property_photos_extract_check = self.check_if_exists(property_photos_extract)
        if property_photos_extract_check is not None:
            property_photos_list = []
            for element in property_photos_extract:
                try:
                    item = self.get_shorter(element, 'jpg')
                    property_photos_list.append(item)
                except:
                    pass
            property_photos = self.store_images(property_photos_list)
            property_photo = property_photos[0]
        else:
            property_photos = None
            property_photo = None
        address_script = self.get_text(script, 'window.__INITIAL_PROPS__', ';', )

        coordinates_data = self.get_list(address_script, '{', '}')
        latitude_extract = self.get_if_element_in(
            coordinates_data, '\\"latitude\\":', ',', 'latitude'
        )
        longitude_extract = self.get_if_element_in(
            coordinates_data, '"longitude\\":', ',', 'longitude'
        )
        latitude = self.check_if_exists(latitude_extract)
        longitude = self.check_if_exists(longitude_extract)
        if latitude is not None and longitude is not None:
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

        property_address_extract = self.get_text(script, 're-Breadcrumb-text">', '</span>')
        property_address_check = self.check_if_exists(property_address_extract)
        property_province_extract = self.get_list(script, 're-Breadcrumb-link"', '</li>')
        property_province_pretty = self.get_text(property_province_extract[1], '>', '<')
        property_province_check = self.check_if_exists(property_province_pretty)
        if property_address_check is not None and property_province_check is not None:
            property_address = unescape(property_address_check + ', ' + property_province_check + ', Spain')
        else:
            property_address = 'Spain'
        property_advertise_type_extract = (
            'Sale' if 'buy' in property_link
            else 'Rent' if 'rental' in property_link
            else 'Other'
        )
        property_advertise_type = self.normalize_advertise_type(property_advertise_type_extract)
        property_renewed = datetime.now().strftime('%d %B %Y')
        property_agency_extract = self.get_text(script, '\\"clientAlias\\":\\"', '\\",\\"clientContactEmail')
        property_agency_check = unescape(self.check_if_exists(property_agency_extract))
        if property_agency_check is not None:
            property_agency = self.get_no_spaces(property_agency_check)
        else:
            property_agency = None
        property_agency_link_extract = self.get_text(script, '"clientUrl\\":\\"', '\\",\\"clientTypeId')
        property_agency_link_check = self.check_if_exists(property_agency_link_extract)
        if property_agency_link_check is not None:
            property_agency_link = website + property_agency_link_check
        else:
            property_agency_link = None
        if property_address is not None and property_type is not None:
            property_slug_combine = property_address + ', ' + property_type
        else:
            property_slug_combine = property_website_country + ', ' + property_type
        property_slug = self.get_slug(property_slug_combine)
        date_time = datetime.utcnow()

        items['property_source_website'] = property_source_website
        items['property_website_country'] = property_website_country
        items['property_link'] = property_link
        items['property_address'] = property_address
        items['property_cost'] = property_cost
        items['property_cost_integer'] = property_cost_integer
        items['property_cost_currency'] = property_cost_currency
        items['property_price'] = property_price
        items['property_bedrooms'] = property_bedrooms
        items['property_bathrooms'] = property_bathrooms
        items['property_square'] = property_square
        items['property_type'] = property_type
        items['property_advertise_type'] = property_advertise_type
        items['property_source_language'] = property_source_language
        items['property_description_source'] = property_description_source
        items['property_features'] = property_features
        items['property_facilities'] = property_facilities
        items['property_coordinates'] = property_coordinates
        items['property_geo'] = property_geo
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

        yield items

    def parse_agency_content(self, response, **kwargs):
        items = AgencyItem()
        agency_source_website = 'https://www.fotocasa.es/en/'
        agency_website_country = 'Spain'
        agency_link = response.url
        agency_script = response.text

        agency_name_extract = self.get_text(agency_script, 'sui-AtomImage-image', '/>')
        agency_name_get = unescape(self.get_text(agency_name_extract, 'title="', '"'))
        agency_name_pretty = self.get_no_spaces(agency_name_get)
        agency_name = self.check_if_exists(agency_name_pretty)

        agency_logo_extract = self.get_text(agency_script, 're-AgencyBanner-logo"', 'alt=')
        agency_logo_get = self.get_text(agency_logo_extract, 'src="', '"')
        agency_logo_check = self.check_if_exists(agency_logo_get)
        if agency_logo_check is not None:
            agency_logo_list = [agency_logo_check]
            agency_logo_store = self.store_images(agency_logo_list)
            agency_logo = agency_logo_store[0]
        else:
            agency_logo = None

        agency_overview_extract = self.get_text(agency_script, 're-AgencyBanner-description">', '<')
        agency_overview_check = self.check_if_exists(agency_overview_extract)
        if agency_overview_check is not None:
            agency_overview = unescape(agency_overview_check)
        else:
            agency_overview = None

        agency_phone_extract = self.get_list(agency_script, 'href="tel:', '"')[1:]
        agency_phone_check = self.check_if_exists(agency_phone_extract)
        if agency_phone_check is not None:
            agency_phone = agency_phone_extract[0]
        else:
            agency_phone = None

        agency_website_extract = self.get_list(agency_script, '"webDomain\\":\\"', '\\"')[1:]
        agency_website_check = self.check_if_exists(agency_website_extract)
        if agency_website_check is not None:
            agency_website = agency_website_check[0]
        else:
            agency_website = None
        try:
            agency_slug = self.get_slug(agency_name)
        except:
            agency_slug = agency_name
        date_time = datetime.utcnow()

        items['agency_source_website'] = agency_source_website
        items['agency_website_country'] = agency_website_country
        items['agency_name'] = agency_name
        items['agency_logo'] = agency_logo
        items['agency_website'] = agency_website
        items['agency_phone'] = agency_phone
        items['agency_link'] = agency_link
        items['agency_overview'] = agency_overview
        items['agency_slug'] = agency_slug
        items['date_time'] = date_time

        logger.info('Yielding new agency item...')
        yield items


class SpainFotocasaScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = SpainFotocasaSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = SpainFotocasaScraper()
    scraper.run_spiders()
