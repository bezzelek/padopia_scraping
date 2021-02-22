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
    property_price = scrapy.Field()
    property_eircode = scrapy.Field()
    property_bedrooms = scrapy.Field()
    property_bathrooms = scrapy.Field()
    property_square = scrapy.Field()
    property_type = scrapy.Field()
    property_advertise_type = scrapy.Field()
    property_source_language = scrapy.Field()
    property_description = scrapy.Field()
    property_description_source = scrapy.Field()
    property_overview = scrapy.Field()
    property_facilities = scrapy.Field()
    property_features = scrapy.Field()
    property_photo = scrapy.Field()
    property_photos = scrapy.Field()
    property_coordinates = scrapy.Field()
    property_geo = scrapy.Field()
    property_renewed = scrapy.Field()
    property_shorter = scrapy.Field()
    property_agent = scrapy.Field()
    property_agent_photo = scrapy.Field()
    property_agency = scrapy.Field()
    property_agency_licence = scrapy.Field()
    property_agency_link = scrapy.Field()
    property_slug = scrapy.Field()
    date_time = scrapy.Field()
    pass


class AgencyItem(scrapy.Item):
    agency_source_website = scrapy.Field()
    agency_website_country = scrapy.Field()
    agency_link = scrapy.Field()
    agency_website = scrapy.Field()
    agency_name = scrapy.Field()
    agency_logo = scrapy.Field()
    agency_overview = scrapy.Field()
    agency_phone = scrapy.Field()
    agency_licence_number = scrapy.Field()
    agency_details = scrapy.Field()
    agency_agents_details = scrapy.Field()
    agency_slug = scrapy.Field()
    date_time = scrapy.Field()
    pass


# p_items['property_source_website'] = property_source_website
# p_items['property_website_country'] = property_website_country
# p_items['property_link'] = property_link
# p_items['property_address'] = property_address
# p_items['property_cost'] = property_cost
# p_items['property_cost_integer'] = property_cost_integer
# p_items['property_cost_currency'] = property_cost_currency
# p_items['property_price'] = property_price
# p_items['property_eircode'] = property_eircode
# p_items['property_bedrooms'] = property_bedrooms
# p_items['property_bathrooms'] = property_bathrooms
# p_items['property_square'] = property_square
# p_items['property_type'] = property_type
# p_items['property_advertise_type'] = property_advertise_type
# p_items['property_source_language'] = property_source_language
# p_items['property_description'] = property_description
# p_items['property_description_source'] = property_description_source
# p_items['property_overview'] = property_overview
# p_items['property_facilities'] = property_facilities
# p_items['property_features'] = property_features
# p_items['property_photo'] = property_photo
# p_items['property_photos'] = property_photos
# p_items['property_coordinates'] = property_coordinates
# p_items['property_geo'] = property_geo
# p_items['property_renewed'] = property_renewed
# p_items['property_shorter'] = property_shorter
# p_items['property_agent'] = property_agent
# p_items['property_agent_photo'] = property_agent_photo
# p_items['property_agency'] = property_agency
# p_items['property_agency_licence'] = property_agency_licence
# p_items['property_agency_link'] = property_agency_link
# p_items['property_slug'] = property_slug
# p_items['date_time'] = date_time


# a_items['agency_source_website'] = agency_source_website
# a_items['agency_website_country'] = agency_website_country
# a_items['agency_link'] = agency_link
# a_items['agency_website'] = agency_website
# a_items['agency_name'] = agency_name
# a_items['agency_logo'] = agency_logo
# a_items['agency_overview'] = agency_overview
# a_items['agency_phone'] = agency_phone
# a_items['agency_licence_number'] = agency_licence_number
# a_items['agency_details'] = agency_details
# a_items['agency_agents_details'] = agency_agents_details
# a_items['agency_slug'] = agency_slug
# a_items['date_time'] = date_time
