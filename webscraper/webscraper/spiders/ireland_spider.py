import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from webscraper.webscraper.items import WebscraperItem
from scrapy_selenium import SeleniumRequest


class IrelandSpider(scrapy.Spider):
    name = 'ireland'
    start_urls = [
        'https://www.daft.ie/ireland/property-for-sale/?s%5Badvanced%5D=1&searchSource=sale&offset=00'
    ]

    def parse(self, response, **kwargs):
        home_page = 'https://www.daft.ie'
        property_urls = response.css(
            "a.PropertyInformationCommonStyles__propertyPrice--link::attr(href)"
        ).extract()
        for url in property_urls:
            property_page = home_page + url
            yield scrapy.Request(property_page, callback=self.parse_property_content)

        # next_url = response.css('li.next_page a::attr(href)').get()
        # next_page = home_page + next_url
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parse)

    def parse_property_content(self, response, **kwargs):
        items = WebscraperItem()

        property_link = response.xpath('/html/head/meta[29]/@content').extract()
        property_address = response.css('.PropertyMainInformation__address::text').extract()
        property_cost = response.css('.PropertyInformationCommonStyles__costAmountCopy::text').extract()
        property_eircode = response.xpath('//div[2]/div/section[1]/div[2]/text()').extract()[1].strip()
        property_bedrooms = response.xpath("//div[@class='QuickPropertyDetails__iconCopy']/text()").extract()
        property_bathrooms = response.xpath(
            "//div[@class='QuickPropertyDetails__iconCopy--WithBorder']/text()").extract()
        property_type = response.xpath("//div[@class='PropertyInformationCommonStyles__quickPropertyDetailsContainer "
                                       "PropertyMainInformation__quickInfo']/div["
                                       "@class='QuickPropertyDetails__propertyType']/text()").extract()[0].strip()
        property_description = response.xpath(
            "normalize-space(/html/body/div[10]/div[2]/div[2]/div/section[3]/p)").extract()
        property_overview = response.xpath(
            "normalize-space(//div[@class='PropertyOverview__propertyOverviewDetails'])").extract()
        property_features = response.xpath("normalize-space(//section[@class='Section__container'][4])").extract()
        property_renewed = response.xpath(
            "normalize-space(//div[@class='PropertyStatistics__iconContainer'][1])").extract()
        property_views = response.xpath(
            "normalize-space(//div[@class='PropertyStatistics__iconContainer'][2])").extract()
        property_shorter = response.xpath(
            "//a[@class='ExpandMoreIndicator__expandLink PropertyShortcode__link']/@href").extract()
        property_agent = response.xpath("//h4[@class='ContactForm__negotiatorName']/text()").extract()
        property_agent_photo = response.xpath("//img[@class='ContactForm__avatar']/@src").extract()
        property_agency_link = response.xpath('/html/body/div[10]/div[2]/div[2]/aside/section/h4/a/@href').get()

        items['property_link'] = property_link
        items['property_address'] = property_address
        items['property_cost'] = property_cost
        items['property_eircode'] = property_eircode
        items['property_bedrooms'] = property_bedrooms
        items['property_bathrooms'] = property_bathrooms
        items['property_type'] = property_type
        items['property_description'] = property_description
        items['property_overview'] = property_overview
        items['property_features'] = property_features
        items['property_renewed'] = property_renewed
        items['property_views'] = property_views
        items['property_shorter'] = property_shorter
        items['property_agent'] = property_agent
        items['property_agent_photo'] = property_agent_photo
        items['property_agency_link'] = property_agency_link

        # if property_agency_link is not None:
        #     SeleniumRequest(url=property_agency_link, callback=self.parse_agency_content)

        yield items

    def parse_agency_content(self, response, **kwargs):
        agency_name = response.xpath('//*[@id="gc_content"]/h1/text()').extract()
        agency_agents = response.xpath('//*[@id="gc_content"]/div[4]/table[1]/tr/text()').extract()
        yield agency_name


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(IrelandSpider)
    process.start()
