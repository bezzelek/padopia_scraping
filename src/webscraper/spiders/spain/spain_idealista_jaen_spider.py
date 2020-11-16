import os

import scrapy

from logging import getLogger
from datetime import datetime
from shutil import which

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_selenium import SeleniumRequest

from src.webscraper.items import PropertyItem
from webscraper.proxies import get_proxies

logger = getLogger()


class SpainIdealistaJaenSpider(scrapy.Spider):
    logger.info('Launching Jaen spider...')
    name = 'IdealistaPropertyJaen'
    start_urls = [
        'https://www.idealista.com/en/venta-viviendas/jaen-provincia/'
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 3,
        # 'DOWNLOAD_TIMEOUT': 10,
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': which('chromedriver'),
        'SELENIUM_DRIVER_ARGUMENTS': ['--headless'],
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 400, 403, 404, 408],

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
            'scrapy_selenium.SeleniumMiddleware': 800,
        },
        'DEFAULT_REQUEST_HEADERS': {
            # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            # 'accept-encoding': 'gzip, deflate, br',
            # 'accept-language': 'en-US,en;q=0.9,uk;q=0.8,ru;q=0.7',
            # 'cache-control': 'no-cache',
            # 'cookie': """userUUID=8d0a0864-60cc-4563-82bf-09d941e38972; _pxhd=726472888aab5634a104e4e4a9953b7baa9bd38461656f44d6598f0f20de8bd8:813d7731-2271-11eb-b49e-d3e4982fe922; cookieDirectiveClosed=true; askToSaveAlertPopUp=true; cookieSearch-1="/venta-viviendas/a-coruna-provincia/:1605188918284"; contact5d458417-52c4-4135-868a-8ea5107b244c="{'email':null,'phone':null,'phonePrefix':null,'friendEmails':null,'name':null,'message':null,'message2Friends':null,'maxNumberContactsAllow':10,'defaultMessage':true}"; send5d458417-52c4-4135-868a-8ea5107b244c="{'friendsEmail':null,'email':null,'message':null}"; SESSION=20e49b7c-125b-419f-b8c3-b54a7d0bc15a; WID=503ae74b1083bcf5|X61gB|X61gB""",
            # 'pragma': 'no-cache',
            # 'referer': 'https://www.idealista.com/en/',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'authority': 'www.idealista.com',
            # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36',
        }
    }

    def parse(self, response, **kwargs):
        logger.info('Starting to scrap...')
        home_page = 'https://www.idealista.com'

        property_page_part = response.xpath('//*[@id="main-content"]/section/article/div/a/@href').extract()
        property_pages_buffer = []
        for link in property_page_part:
            property_page = home_page + link
            property_pages_buffer.append(property_page)

        """Going to property page"""
        for link in property_pages_buffer:
            logger.info('Going to property page...')
            yield SeleniumRequest(url=link, callback=self.parse_property_content, priority=100)

        """Follow the pagination"""
        next_url_part = response.xpath('//*[@id="main-content"]/section/div/ul/li[@class="next"]/a/@href').get()
        if next_url_part is not None:
            next_url = home_page + next_url_part
            logger.info('Following pagination and going to nex page...')
            yield response.follow(next_url, callback=self.parse, priority=10)

    def parse_property_content(self, response, **kwargs):
        logger.info('Scraping property page...')
        items = PropertyItem()
        website_url = 'https://www.idealista.com'

        """Extracting data"""
        property_source_website = 'https://www.idealista.com/'
        property_website_country = 'Spain'
        property_link = response.url
        property_address_extract = response.xpath('//*[@id="headerMap"]/ul/li/text()').extract()
        property_address = ''.join(property_address_extract).strip()
        property_cost_extract = response.xpath(
            '//*[@id="mortgages"]/div[2]/div/article/section/p[1]/strong/text()').extract()
        property_cost = ''.join(property_cost_extract).strip()
        property_cost_integer = ''.join([number for number in property_cost if number.isdigit()])
        property_cost_currency = property_cost[-1]
        property_bedrooms_extract = response.xpath(
            '//p[@class="info-data txt-big"]/span[2]/span/text()').extract()  # //div[@class="info-features"]/span[2]/span/text()
        property_bedrooms = ''.join(property_bedrooms_extract).strip()
        property_bathrooms_extract = ''.join([
            text.get()
            for text in response.xpath('//script/text()')
            if 'var utag_data =' in text.get()
        ])
        property_bathrooms = property_bathrooms_extract.split('bathNumber":"')[1].split('"')[0]
        property_square_extract = response.xpath('//p[@class="info-data txt-big"]/span[1]/span/text()').extract()
        property_square = ''.join(property_square_extract).strip()
        property_type_extract = response.xpath('//div[@class="main-info"]/strong/text()').extract()
        property_type = ''.join(property_type_extract).strip()
        property_description_extract = response.xpath('//div[@class="adCommentsLanguage expandable"]/text()').extract()
        property_description = ''.join(property_description_extract).strip()
        property_facilities_extract = response.xpath('//*[@id="details"]/div/div[2]/div/ul/li/text()').extract()
        property_facilities = ''.join(property_facilities_extract).strip()
        property_features_extract = response.xpath('//*[@id="details"]/div/div[1]/div/ul/li/text()').extract()
        property_features = ''.join(property_features_extract).strip()
        property_script = ''.join([
            text.get()
            for text in response.xpath('//script/text()')
            if 'var config=' in text.get()
        ])
        property_photos = [
            image.split(',')[0]
            for image in property_script.split('imageDataService:"')
        ][1:]
        property_photo = property_photos[0]
        property_coordinates = {
            'latitude': property_script.split('latitude:"')[1].split('"')[0],
            'longitude': property_script.split('longitude:"')[1].split('"')[0],
        }
        property_renewed_extract = response.xpath('//*[@id="stats"]/p/text()').extract()
        property_renewed = ''.join(property_renewed_extract).strip()
        property_agent_extract = response.xpath("//div/a[@class='about-advertiser-name']/text()").extract()
        property_agent = ''.join(property_agent_extract).strip()
        property_agent_photo_extract = response.xpath("//div[@class='advertiser-logo']/a/img/@src").extract()
        property_agent_photo = ''.join(property_agent_photo_extract).strip()
        property_agency_link_extract = response.xpath("//div/a[@class='about-advertiser-name']/@href").get()
        property_agency_link = website_url + property_agency_link_extract

        property_address_lower = property_address.lower()
        punctuation = "!@#$%^&*()_-+<>?:.,;"
        for symbol in property_address_lower:
            if symbol in punctuation:
                property_address_lower = property_address_lower.replace(symbol, "")
        property_slug = property_address_lower.replace(" ", "-")
        date_time = datetime.utcnow()

        """Preparing items for db"""
        items['property_source_website'] = property_source_website
        items['property_website_country'] = property_website_country
        items['property_link'] = property_link
        items['property_address'] = property_address
        items['property_cost'] = property_cost
        items['property_cost_integer'] = property_cost_integer
        items['property_cost_currency'] = property_cost_currency
        items['property_bedrooms'] = property_bedrooms
        items['property_bathrooms'] = property_bathrooms
        items['property_square'] = property_square
        items['property_type'] = property_type
        items['property_description'] = property_description
        items['property_facilities'] = property_facilities
        items['property_features'] = property_features
        items['property_photo'] = property_photo
        items['property_photos'] = property_photos
        items['property_coordinates'] = property_coordinates
        items['property_renewed'] = property_renewed
        items['property_agent'] = property_agent
        items['property_agent_photo'] = property_agent_photo
        items['property_agency_link'] = property_agency_link
        items['property_slug'] = property_slug
        items['date_time'] = date_time

        # """Go to agency page"""
        # if property_agency_link is not None:
        #     logger.info('Going to agency page...')
        #     yield SeleniumRequest(url=property_agency_link, callback=self.parse_agency_content, priority=200)

        logger.info('Yielding new property item...')
        yield items


class SpainIdealistaJaenScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = SpainIdealistaJaenSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = SpainIdealistaJaenScraper()
    scraper.run_spiders()
