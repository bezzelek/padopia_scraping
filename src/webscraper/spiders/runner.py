"""runner"""
# import os
#
# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings
#
# from src.webscraper.spiders.ireland_daft_spider import IrelandDaftSpider
#
#
# class IrelandDaftScraper:
#     def __init__(self):
#         settings_file_path = 'webscraper.settings'
#         os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
#         self.process = CrawlerProcess(get_project_settings())
#         self.spider = IrelandDaftSpider
#
#     def run_spiders(self):
#         self.process.crawl(self.spider)
#         self.process.start()
#
#
# if __name__ == "__main__":
#     scraper = IrelandDaftScraper()
#     scraper.run_spiders()
