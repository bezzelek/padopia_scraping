import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from src.webscraper.items import PropertyItem, AgencyItem
from scrapy_selenium import SeleniumRequest


class IrelandSpider(scrapy.Spider):
    name = 'ireland'
    start_urls = [
        'https://www.daft.ie/ireland/property-for-sale/?s%5Badvanced%5D=1&searchSource=sale&offset=00'
    ]

    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'data.json'
    }

    def parse(self, response, **kwargs):
        home_page = 'https://www.daft.ie'
        property_urls = response.css(
            "a.PropertyInformationCommonStyles__propertyPrice--link::attr(href)"
        ).extract()
        for url in property_urls:
            property_page = home_page + url
            yield scrapy.Request(url=property_page, callback=self.parse_property_content)

        # next_url = response.css('li.next_page a::attr(href)').get()
        # next_page = home_page + next_url
        # if next_page is not None:
        #     yield response.follow(next_page, callback=self.parse)

    def parse_property_content(self, response, **kwargs):
        items = PropertyItem()

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

        property_photo = response.xpath('//*[@id="pbxl_carousel"]/ul/li[1]/img/@src').extract()
        property_photos = response.xpath('//*[@id="pbxl_carousel"]/ul/li/img/@src').extract()
        property_renewed = response.xpath(
            '//div[1]/div[@class="PropertyStatistics__iconData"][1]/text()').extract()
        property_shorter = response.xpath(
            "//a[@class='ExpandMoreIndicator__expandLink PropertyShortcode__link']/@href").extract()

        property_agent = response.xpath("//h4[@class='ContactForm__negotiatorName']/text()").extract()
        property_agent_photo = response.xpath("//aside/div[1]/div/div[1]/div/img/@src").extract()
        property_agency_licence = response.xpath('//aside/section/div[3]/span/text()').extract()
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

        if property_agency_link is not None:
            yield SeleniumRequest(url=property_agency_link, callback=self.parse_agency_content)

        yield items

    def parse_agency_content(self, response, **kwargs):
        items = AgencyItem()

        agency_name = response.xpath('//*[@id="gc_content"]/h1/text()').extract()
        agency_logo = response.xpath('/html/body/div[6]/img/@src').get()

        agency_overview_extract = response.xpath(
            '//*[@id="gc_links"]/p/text() | //*[@id="gc_links"]/p/a/text()').extract()
        agency_overview = ''.join(agency_overview_extract).strip()

        agency_licence_extract = response.xpath('//*[@id="gc_links"]/text()').extract()
        agency_licence_info = ''.join(agency_licence_extract).strip()
        agency_licence_number = ''.join([number for number in agency_licence_info if number.isdigit()])

        agency_details_extract = response.xpath('//*[@id="gc_content"]/p/text()').extract()
        agency_details = ''.join(agency_details_extract).strip()

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

        items['agency_name'] = agency_name
        items['agency_logo'] = agency_logo
        items['agency_overview'] = agency_overview
        items['agency_licence_number'] = agency_licence_number
        items['agency_details'] = agency_details
        items['agency_agents_details'] = agency_agents_details

        yield items


if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(IrelandSpider)
    process.start()
