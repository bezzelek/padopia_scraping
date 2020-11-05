import scrapy

from logging import getLogger
from datetime import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from src.webscraper.items import PropertyItem, AgencyItem
from scrapy_selenium import SeleniumRequest
from apscheduler.schedulers.twisted import TwistedScheduler


logger = getLogger()


class IrelandSpider(scrapy.Spider):
    logger.info('Launching Ireland spider...')
    name = 'ireland'
    start_urls = [
        'https://www.daft.ie/ireland/property-for-sale/?s%5Badvanced%5D=1&searchSource=sale&offset=00'
    ]

    """JSON output just for testing"""
    # custom_settings = {
    #     'FEED_FORMAT': 'json',
    #     'FEED_URI': 'data.json'
    # }

    def parse(self, response, **kwargs):
        logger.info('Starting to scrap...')
        home_page = 'https://www.daft.ie'
        property_urls = response.css(
            "a.PropertyInformationCommonStyles__propertyPrice--link::attr(href)"
        ).extract()
        for url in property_urls:
            property_page = home_page + url
            logger.info('Going to property page...')
            yield scrapy.Request(url=property_page, callback=self.parse_property_content)

        """Follow the pagination"""
        next_url = response.css('li.next_page a::attr(href)').get()
        next_page = home_page + next_url
        if next_page is not None:
            logger.info('Following pagination and going to nex page...')
            yield response.follow(next_page, callback=self.parse)

    def parse_property_content(self, response, **kwargs):
        logger.info('Scraping property page...')
        items = PropertyItem()

        property_link_extract = response.xpath('/html/head/meta[29]/@content').extract()
        property_link = ''.join(property_link_extract).strip()
        property_address_extract = response.css('.PropertyMainInformation__address::text').extract()
        property_address = ''.join(property_address_extract).strip()
        property_cost_extract = response.css('.PropertyInformationCommonStyles__costAmountCopy::text').extract()
        property_cost = ''.join(property_cost_extract).strip()
        property_cost_integer = ''.join([number for number in property_cost if number.isdigit()])
        property_cost_currency = property_cost[0]
        property_eircode = response.xpath('//div[2]/div/section[1]/div[2]/text()').extract()[1].strip()
        property_bedrooms_extract = response.xpath("//div[@class='QuickPropertyDetails__iconCopy']/text()").extract()
        property_bedrooms = ''.join(property_bedrooms_extract).strip()
        property_bathrooms_extract = response.xpath(
            "//div[@class='QuickPropertyDetails__iconCopy--WithBorder']/text()").extract()
        property_bathrooms = ''.join(property_bathrooms_extract).strip()
        property_type = response.xpath("//div[@class='PropertyInformationCommonStyles__quickPropertyDetailsContainer "
                                       "PropertyMainInformation__quickInfo']/div["
                                       "@class='QuickPropertyDetails__propertyType']/text()").extract()[0].strip()
        property_description_extract = response.xpath(
            "/html/body/div[10]/div/div[2]/div/section/p/text()").extract()
        property_description = ''.join(property_description_extract).strip()
        property_overview_extract = response.xpath(
            "//div[@class='PropertyOverview__propertyOverviewDetails']/text()").extract()
        property_overview = ''.join(property_overview_extract).strip()
        property_facilities_extract = response.xpath(
            "//li[@class='PropertyFacilities__iconWithText']/span[@class='PropertyFacilities__iconText']/text()"
        ).extract()
        property_facilities = ''.join(property_facilities_extract).strip()
        property_features_extract = response.xpath("//ul/li/span/text()").extract()
        property_features = ''.join(property_features_extract).strip()
        property_photo_extract = response.xpath('//*[@id="pbxl_carousel"]/ul/li[1]/img/@src').extract()
        property_photo = ''.join(property_photo_extract).strip()
        property_photos = response.xpath('//*[@id="pbxl_carousel"]/ul/li/img/@src').extract()
        property_renewed_extract = response.xpath(
            '//div[1]/div[@class="PropertyStatistics__iconData"][1]/text()').extract()
        property_renewed = ''.join(property_renewed_extract).strip()
        property_shorter_extract = response.xpath(
            "//a[@class='ExpandMoreIndicator__expandLink PropertyShortcode__link']/@href").extract()
        property_shorter = ''.join(property_shorter_extract).strip()

        property_agent_extract = response.xpath("//h4[@class='ContactForm__negotiatorName']/text()").extract()
        property_agent = ''.join(property_agent_extract).strip()
        property_agent_photo_extract = response.xpath("//aside/div[1]/div/div[1]/div/img/@src").extract()
        property_agent_photo = ''.join(property_agent_photo_extract).strip()
        property_agency_licence_extract = response.xpath('//aside/section/div[3]/span/text()').extract()
        property_agency_licence = ''.join(property_agency_licence_extract).strip()
        property_agency_link = response.xpath('/html/body/div[10]/div[2]/div[2]/aside/section/h4/a/@href').get()
        date_time = datetime.utcnow()

        items['property_link'] = property_link
        items['property_address'] = property_address
        items['property_cost'] = property_cost
        items['property_cost_integer'] = property_cost_integer
        items['property_cost_currency'] = property_cost_currency
        items['property_eircode'] = property_eircode
        items['property_bedrooms'] = property_bedrooms
        items['property_bathrooms'] = property_bathrooms
        items['property_type'] = property_type
        items['property_description'] = property_description
        items['property_overview'] = property_overview
        items['property_facilities'] = property_facilities
        items['property_features'] = property_features
        items['property_photo'] = property_photo
        items['property_photos'] = property_photos
        items['property_renewed'] = property_renewed
        items['property_shorter'] = property_shorter
        items['property_agent'] = property_agent
        items['property_agent_photo'] = property_agent_photo
        items['property_agency_licence'] = property_agency_licence
        items['property_agency_link'] = property_agency_link
        items['date_time'] = date_time

        """Go to agency page"""
        if property_agency_link is not None:
            logger.info('Going to agency page...')
            yield SeleniumRequest(url=property_agency_link, callback=self.parse_agency_content)

        logger.info('Yielding new property item...')
        yield items

    def parse_agency_content(self, response, **kwargs):
        logger.info('Scraping agency page...')
        items = AgencyItem()

        agency_name_extract = response.xpath('//*[@id="gc_content"]/h1/text()').extract()
        agency_name = ''.join(agency_name_extract).strip()
        agency_logo = response.xpath('/html/body/div[6]/img/@src').get()
        agency_link = response.xpath('/html/head/link[1]/@href').get()

        agency_overview_extract = response.xpath(
            '//*[@id="gc_links"]/p/text() | //*[@id="gc_links"]/p/a/text()').extract()
        agency_overview = ''.join(agency_overview_extract).strip()

        agency_licence_extract = response.xpath('//*[@id="gc_links"]/text()').extract()
        agency_licence_info = ''.join(agency_licence_extract).strip()
        agency_licence_number = ''.join([number for number in agency_licence_info if number.isdigit()])

        agency_details_extract = response.xpath('//*[@id="gc_content"]/p/text()').extract()
        agency_details = ''.join(agency_details_extract).strip()

        """Scrap table"""
        agency_agents_details = {
            'name': [],
            'phone': [],
            'add_info': []
        }
        response_table = iter(response.xpath('//*[@id="gc_content"]/div[4]/table[1]/tr'))
        next(response_table)
        for row in response_table:
            name = row.xpath('normalize-space(td[1])').get()
            phone = row.xpath('normalize-space(td[2])').get()
            add_info = row.xpath('normalize-space(td[3])').get()
            agency_agents_details['name'].append(name)
            agency_agents_details['phone'].append(phone)
            agency_agents_details['add_info'].append(add_info)
        date_time = datetime.utcnow()

        items['agency_name'] = agency_name
        items['agency_logo'] = agency_logo
        items['agency_link'] = agency_link
        items['agency_overview'] = agency_overview
        items['agency_licence_number'] = agency_licence_number
        items['agency_details'] = agency_details
        items['agency_agents_details'] = agency_agents_details
        items['date_time'] = date_time

        logger.info('Yielding new agency item...')
        yield items


"""Launch script"""
if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    """Scheduler to run task periodically"""
    # scheduler = TwistedScheduler()
    # scheduler.add_job(process.crawl, 'interval', args=[IrelandSpider], seconds=60*60*24)
    # scheduler.start()
    # process.start(False)
    process.crawl(IrelandSpider)
    process.start()
