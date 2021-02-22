import json

import dns
import pymongo

from bson.son import SON
from bson import ObjectId
from datetime import datetime
from bson.json_util import dumps

from pymongo import MongoClient, GEOSPHERE

from src.webscraper.settings import DB_CONNECTION


def create_mongodb_geo_object():
    """Connecting to DB and geo service"""
    connection = MongoClient(DB_CONNECTION)
    db = connection['padopiadata']
    collection_property = db['property']

    """Getting number of properties without mongodb geolocation object"""
    query = {
        '$and': [
            {'property_coordinates.latitude': {'$exists': True}},
            {'property_coordinates.longitude': {'$exists': True}},
            {'property_geo': {'$exists': False}}
        ]
    }

    number_of_docs = collection_property.count_documents(query)

    """Log"""
    print(f'Work started! There are {number_of_docs} records to process...')

    """Processed documents"""
    processed_documents = []
    for number in range(number_of_docs):
        """Extracting document without geolocation object"""
        document = extracting_document(number, number_of_docs, collection_property, query)
        processed_documents.append(document['log_id'])

        """Extracting coordinates from document"""
        item_coordinates = extracting_coordinates(document['item'], document['log_id'])

        """Converting coordinates to mongodb object"""
        mongo_geo_object = converting_to_mongo_format(item_coordinates, document['log_id'])

        """Updating database record"""
        updating_db_record(collection_property, document['item_id'], document['log_id'], mongo_geo_object)

    print(f'Work done! {len(processed_documents)} documents processed of {number_of_docs}.')


def extracting_document(number, number_of_docs, collection_property, query):
    """Log"""
    print(f'Starting to process record #{number} of {number_of_docs}...')

    """Getting document geo object"""
    item_search = collection_property.find(query).skip(number).limit(1)

    item = json.loads(dumps(item_search))

    item_id = item[0]['_id']['$oid']
    log_id = str(item_id)

    result = {'item': item, 'item_id': item_id, 'log_id': log_id}

    return result


def extracting_coordinates(item, log_id):
    """Extracting coordinates"""
    try:
        item_coordinates = [
            float(item[0]['property_coordinates']['longitude']),
            float(item[0]['property_coordinates']['latitude']),
        ]

        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| Coordinates extracted from document. Values are {item_coordinates}...'
        })

        return item_coordinates

    except:
        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR while extracting coordinates from document. There is no lon or lat value...'
        })

        item_coordinates = None

        return item_coordinates


def converting_to_mongo_format(item_coordinates, log_id):
    """Converting values to mongodb object"""
    if item_coordinates is None:
        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR because coordinates are {item_coordinates}...'
        })
        return None

    else:
        """Converting"""
        mongo_geo_object = {'property_geo': {'type': 'Point', 'coordinates': item_coordinates}}

        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| Coordinates converted. Objects is {mongo_geo_object}...'
        })

        return mongo_geo_object


def updating_db_record(collection_property, item_id, log_id, mongo_geo_object):
    if mongo_geo_object is not None:
        """Updating property document"""
        collection_property.update_one(
            {
                '_id': ObjectId(item_id)
            },
            {
                '$set': mongo_geo_object
            }
        )

        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| Record updated successfully!'
        })

    else:
        """log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR while updating document!!!'
        })


if __name__ == "__main__":
    create_mongodb_geo_object()
