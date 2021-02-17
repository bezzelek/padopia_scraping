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


logger = getLogger()


class TestSpider(scrapy.Spider, Normalization, UploadPhoto):
    logger.info('Test spider...')
    name = 'Test'
    start_urls = [
        'https://www.yaencontre.com/venta/pisos/madrid-provincia'
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

    #     logger.info('Starting to scrap...')
    #     body_extract = response.text
    #     sitemap_extract = self.get_list(body_extract, '<loc>', '</loc>')[1:]
    #
    #     sitemap_records = []
    #     for element in sitemap_extract:
    #         if 'detail' in element:
    #             sitemap_records.append(element)
    #
    #     sitemap_sale = []
    #     for element in sitemap_records:
    #         if 'satilik' in element:
    #             link = element
    #             number = int(self.get_text(element, 'p_', '.xml'))
    #             item = {
    #                 'link': link,
    #                 'number': number,
    #             }
    #             sitemap_sale.append(item)
    #
    #     sitemap_rent = []
    #     for element in sitemap_records:
    #         if 'kiralik' in element:
    #             link = element
    #             number = int(self.get_text(element, 'p_', '.xml'))
    #             item = {
    #                 'link': link,
    #                 'number': number,
    #             }
    #             sitemap_rent.append(item)
    #
    #     max_sale_item = max(sitemap_sale, key=itemgetter('number'))
    #     max_sale = max_sale_item['link']
    #     max_rent_item = max(sitemap_rent, key=itemgetter('number'))
    #     max_rent = max_rent_item['link']
    #
    #     links = [max_sale, max_rent]
    #
    #     for link in links:
    #         yield scrapy.Request(url=link, callback=self.parse_sitemap)
    #
    # def parse_sitemap(self, response, **kwargs):
    #     body_extract = response.text
    #     sitemap_extract = self.get_list(body_extract, '<loc>', '</loc>')[1:]
    #     for link in sitemap_extract:
    #         yield scrapy.Request(url=link, callback=self.parse_property_content)

        # logger.info('Starting to scrap...')
        # property_urls = response.xpath('//div[@class="ej74 ej110 ej166 _25Z8c"]/div/div/a/@href').extract()
        # for link in property_urls:
        #     logger.info('Going to property page...')
        #     next_link = 'https://www.emlakjet.com' + link
        #     yield scrapy.Request(url=next_link, callback=self.parse_property_content, priority=200)
        #
        # """Follow the pagination"""
        # next_page_url = response.xpath('//li[@class="_3vAxf _16xRl"]/div/a/@href').get()
        # if next_page_url is not None:
        #     next_page = 'https://www.emlakjet.com' + next_page_url
        #     logger.info('Following pagination and going to next page...')
        #     yield response.follow(next_page, callback=self.parse)

        # number_of_pages_extract = response.xpath('//div/section/ul/li[8]/a').extract()
        # number_of_pages = int(self.get_text(number_of_pages_extract[0], 'in ', ' '))
        # pagination_list = list(range(2, number_of_pages))
        # for page in pagination_list:
        #     pagination_url = 'https://www.hurriyetemlak.com/satilik?page='
        #     next_page = pagination_url + str(page)
        #     yield response.follow(next_page, callback=self.parse, priority=10)

        #
        # next_page_url = response.xpath().get()
        # if next_page_url is not None:
        #     next_page = 'https://www.grekodom.com' + next_page_url
        #     logger.info('Following pagination and going to next page...')
        #     yield response.follow(next_page, callback=self.parse)

    def parse_property_content(self, response, **kwargs):
        p_items = PropertyItem()

        property_source_website = 'https://www.yaencontre.com/'
        property_website_country = 'Spain'
        property_link = response.url
        property_cost = self.get_text(response.text, '"price\\":', ',')
        # property_script = self.get_text(response.text, 'id="__NEXT_DATA__"', 'script>')
        # property_script_clean = self.get_text(property_script, 'json">', '</')
        # data = json.loads(property_script_clean)

        p_items['property_source_website'] = property_source_website
        p_items['property_website_country'] = property_website_country
        p_items['property_link'] = property_link
        p_items['property_cost'] = property_cost

        yield p_items


class TestScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = TestSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = TestScraper()
    scraper.run_spiders()
