import time
import json

import dns
import pymongo

from bson import ObjectId
from datetime import datetime
from bson.json_util import dumps

from pymongo import MongoClient
from geopy.geocoders import Nominatim

from src.webscraper.settings import DB_CONNECTION


def accurate_address():

    """Connecting to DB and geo service"""
    connection = MongoClient(DB_CONNECTION)
    db = connection['padopiadata']
    collection_property = db['property']

    geolocator = Nominatim(user_agent="padopia")

    """Getting number of properties without accurate address"""
    number_of_docs = collection_property.count_documents({
        '$and': [
            {'property_coordinates.latitude': {'$exists': True}},
            {'property_coordinates.longitude': {'$exists': True}},
            {'property_address_detailed': {'$exists': False}}
        ]
    })

    """Log"""
    print(f'Work started! There are {number_of_docs} records to process...')

    """Processed documents"""
    processed_documents = []
    for number in range(number_of_docs):

        """Extracting documents without detailed address"""
        document = extracting_document(number, number_of_docs, collection_property)
        processed_documents.append(document['log_id'])

        """Extracting coordinates from document"""
        item_coordinates = extracting_coordinates(document['item'], document['log_id'])

        """Requesting detailed address"""
        get_address = get_detailed_address(item_coordinates, document['log_id'], geolocator)

        """Extracting values from response"""
        strict_address_dict = extracting_data_from_geo(get_address, document['log_id'])

        """Updating detailed address to database record"""
        updating_db_record(collection_property, document['item_id'], strict_address_dict, document['log_id'])

    print(f'Work done! {len(processed_documents)} documents processed of {number_of_docs}.')


def extracting_document(number, number_of_docs, collection_property):
    """Log"""
    print(f'Starting to process record #{number} of {number_of_docs}...')

    """Getting document without accurate address"""
    item_search = collection_property.find({
        '$and': [
            {'property_coordinates.latitude': {'$exists': True}},
            {'property_coordinates.longitude': {'$exists': True}},
            {'property_address_detailed': {'$exists': False}}
        ]
    }).skip(number).limit(1)

    item = json.loads(dumps(item_search))

    item_id = item[0]['_id']['$oid']
    log_id = str(item_id)

    result = {'item': item, 'item_id': item_id, 'log_id': log_id}

    return result


def extracting_coordinates(item, log_id):
        """Extracting coordinates"""
        try:
            item_coordinates = [
                item[0]['property_coordinates']['latitude'],
                item[0]['property_coordinates']['longitude'],
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


def get_detailed_address(item_coordinates, log_id, geolocator):
    if item_coordinates is None:
        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR because coordinates are {item_coordinates}...'
        })
        return None

    else:
        try:
            """Getting address"""
            get_address = geolocator.reverse(item_coordinates, language='en', addressdetails=True, zoom=18)

            """Log"""
            print({
                datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                    f'{log_id} ||| Address extracted. It is {get_address}...'
            })

            return get_address

        except:
            print({
                datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR because geolocator cant convert {item_coordinates}...'
            })
            return None


def extracting_data_from_geo(get_address, log_id):
    if get_address is not None:
        """Extracting address from response"""
        strict_address_extract = get_address.raw
        strict_address_dict = strict_address_extract['address']
        strict_address_dict['full_address'] = strict_address_extract['display_name']
        strict_address_dict['coordinates'] = {
            'latitude': strict_address_extract['lat'],
            'longitude': strict_address_extract['lon'],
        }
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| Address extracted successfully from {get_address}...'
        })
        return strict_address_dict
    else:
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR while extracting data from {get_address}...'
        })
        return None


def updating_db_record(collection_property, item_id, strict_address_dict, log_id):
    if strict_address_dict is not None:
        """Updating property document"""
        collection_property.update_one(
            {
                '_id': ObjectId(item_id)
            },
            {
                '$set':
                    {
                        'property_address_detailed': strict_address_dict,
                    }
            }
        )

        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| Record updated successfully!'
        })

        """Cooldown to avoid throttling"""
        time.sleep(0.5)

    else:
        """log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR while getting address from coordinates!!!'
        })

        """Cooldown to avoid throttling"""
        time.sleep(0.5)


if __name__ == "__main__":
    accurate_address()
