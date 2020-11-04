import pymongo
from datetime import datetime, timedelta
from logging import getLogger

from pymongo import MongoClient

from src.webscraper.items import PropertyItem
from src.webscraper.settings import DB_CONNECTION


logger = getLogger()


class PropertyPipeline(object):

    def __init__(self):
        logger.info('Connecting to db...')
        connection = MongoClient(DB_CONNECTION)
        db = connection['padopiadata']
        self.collection_property = db['property']
        self.collection_agencies = db['agencies']

    def process_item(self, item, spider):
        """Delete old records from db"""
        logger.info('Deleting old records...')
        # yesterday = datetime.utcnow() - timedelta(days=1)
        past_hour = datetime.utcnow() - timedelta(minutes=60)
        self.collection_property.remove({"date_time": {"$lt": past_hour}})

        """If we receive property items we put them to property collection"""
        if isinstance(item, PropertyItem):
            """Check if element exist. Update if yes"""
            logger.info('Checking if scraped property already exists...')
            property_link_item = item['property_link']
            find_record = self.collection_property.find({"property_link": {"$eq": property_link_item}})
            check_record = find_record.count()
            if check_record > 0:
                logger.info('Updating existing property...')
                self.collection_property.update_one({"property_link": {"$eq": property_link_item}},
                                                    {"$set": dict(item)})
            else:
                """Put new property item to db"""
                logger.info('Adding new property to database...')
                self.collection_property.insert(dict(item))

        else:
            """If we receive agency items we put them to agency collection"""
            """Check if element exist. Update if yes"""
            logger.info('Checking if scraped agency already exists...')
            agency_name_item = item['agency_name']
            find_record = self.collection_agencies.find({"agency_name": {"$eq": agency_name_item}})
            check_record = find_record.count()
            if check_record > 0:
                logger.info('Updating existing agency...')
                self.collection_agencies.update_one({"agency_name": {"$eq": agency_name_item}},
                                                    {"$set": dict(item)})
            else:
                """Put new agency item to db"""
                logger.info('Adding new agency to database...')
                self.collection_agencies.insert(dict(item))
