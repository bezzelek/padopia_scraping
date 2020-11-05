"""runner"""
from apscheduler.schedulers.twisted import TwistedScheduler
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from src.webscraper.spiders.ireland_spider import IrelandSpider

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    """Scheduler to run task periodically"""
    scheduler = TwistedScheduler()
    scheduler.add_job(process.crawl, 'interval', args=[IrelandSpider], seconds=60*60*24)
    scheduler.start()
    process.start(False)
    # process.crawl(IrelandSpider)
    # process.start()
