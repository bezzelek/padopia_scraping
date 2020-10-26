# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WebscraperItem(scrapy.Item):
    # define the fields for your item here like:

    property_link = scrapy.Field()
    property_address = scrapy.Field()
    property_cost = scrapy.Field()
    property_eircode = scrapy.Field()
    property_bedrooms = scrapy.Field()
    property_bathrooms = scrapy.Field()
    property_type = scrapy.Field()
    property_description = scrapy.Field()
    property_overview = scrapy.Field()
    property_features = scrapy.Field()
    property_renewed = scrapy.Field()
    property_views = scrapy.Field()
    property_shorter = scrapy.Field()
    property_agent = scrapy.Field()
    property_agent_photo = scrapy.Field()
    property_agency_link = scrapy.Field()

    pass
