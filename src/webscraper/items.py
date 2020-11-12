# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PropertyItem(scrapy.Item):
    property_source_website = scrapy.Field()
    property_website_country = scrapy.Field()
    property_link = scrapy.Field()
    property_address = scrapy.Field()
    property_cost = scrapy.Field()
    property_cost_integer = scrapy.Field()
    property_cost_currency = scrapy.Field()
    property_eircode = scrapy.Field()
    property_bedrooms = scrapy.Field()
    property_bathrooms = scrapy.Field()
    property_square = scrapy.Field()
    property_type = scrapy.Field()
    property_description = scrapy.Field()
    property_overview = scrapy.Field()
    property_facilities = scrapy.Field()
    property_features = scrapy.Field()
    property_photo = scrapy.Field()
    property_photos = scrapy.Field()
    property_coordinates = scrapy.Field()
    property_renewed = scrapy.Field()
    property_shorter = scrapy.Field()
    property_agent = scrapy.Field()
    property_agent_photo = scrapy.Field()
    property_agency_licence = scrapy.Field()
    property_agency_link = scrapy.Field()
    property_slug = scrapy.Field()
    date_time = scrapy.Field()
    pass


class AgencyItem(scrapy.Item):
    agency_source_website = scrapy.Field()
    agency_website_country = scrapy.Field()
    agency_name = scrapy.Field()
    agency_logo = scrapy.Field()
    agency_link = scrapy.Field()
    agency_overview = scrapy.Field()
    agency_phone = scrapy.Field()
    agency_licence_number = scrapy.Field()
    agency_details = scrapy.Field()
    agency_agents_details = scrapy.Field()
    agency_slug = scrapy.Field()
    date_time = scrapy.Field()
    pass
