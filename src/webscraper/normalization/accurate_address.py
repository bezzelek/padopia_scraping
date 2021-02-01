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
    print('Work started! There are ' + str(number_of_docs) + ' records to process...')

    """Processed documents"""
    processed_documents = []

    for number in range(number_of_docs):
        """Log"""
        print('Starting to process record #' + str(number) + ' of ' + str(number_of_docs) + '...')

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

        processed_documents.append(log_id)

        """Extracting coordinates from document"""
        try:
            item_coordinates = [
                item[0]['property_coordinates']['latitude'],
                item[0]['property_coordinates']['longitude'],
            ]

            """Log"""
            print({
                datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                    log_id + ' ||| Coordinates extracted from document. Values are ' + str(item_coordinates) + '...'
            })

        except:
            """Log"""
            print({
                datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                    log_id + ' ||| ERROR while extracting coordinates from document. There is no lon or lat value...'
            })

            item_coordinates = None

        if item_coordinates is None:
            """Log"""
            print({
                datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                    log_id + ' ||| ERROR because coordinates are ' + str(item_coordinates) + '...'
            })

        else:
            try:
                """Log"""
                # print({
                #     datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                #         log_id + ' ||| Getting address...'
                # })

                """Getting address"""
                get_address = geolocator.reverse(item_coordinates, language='en', addressdetails=True, zoom=18)

                """Log"""
                print({
                    datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                        log_id + ' ||| Address extracted. It is ' + str(get_address) + '...'
                })

                """Extracting address from response"""
                strict_address_extract = get_address.raw
                strict_address_dict = strict_address_extract['address']

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
                        log_id + ' ||| Record updated successfully!'
                })

                """Cooldown to avoid throttling"""
                time.sleep(0.5)

            except:
                """log"""
                print({
                    datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                        log_id + ' ||| ERROR while getting address from coordinates!!!'
                })

                """Cooldown to avoid throttling"""
                time.sleep(0.5)

    print('Work done')


if __name__ == "__main__":
    accurate_address()
