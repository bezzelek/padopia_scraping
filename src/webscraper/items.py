# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PropertyItem(scrapy.Item):
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
    property_facilities = scrapy.Field()
    property_features = scrapy.Field()
    property_photo = scrapy.Field()
    property_photos = scrapy.Field()
    property_renewed = scrapy.Field()
    property_shorter = scrapy.Field()
    property_agent = scrapy.Field()
    property_agent_photo = scrapy.Field()
    property_agency_licence = scrapy.Field()
    property_agency_link = scrapy.Field()
    date_time = scrapy.Field()
    pass


class AgencyItem(scrapy.Item):
    agency_name = scrapy.Field()
    agency_logo = scrapy.Field()
    agency_overview = scrapy.Field()
    agency_licence_number = scrapy.Field()
    agency_details = scrapy.Field()
    agency_agents_details = scrapy.Field()
    date_time = scrapy.Field()
    pass
