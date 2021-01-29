import time

import dns
import pymongo

from bson import ObjectId
from datetime import datetime

from pymongo import MongoClient
from geopy.geocoders import Nominatim

from src.webscraper.settings import DB_CONNECTION


def accurate_address():

    """Connecting to DB and geo service"""
    connection = MongoClient(DB_CONNECTION)
    db = connection['padopiadata']
    collection_property = db['property']

    geolocator = Nominatim(user_agent="padopia")

    """Searching for property without accurate address"""
    search = collection_property.find({
        '$and': [
            {'property_coordinates': {'$exists': True}},
            {'property_address_detailed': {'$exists': False}}
        ]
    })

    for item in search:

        """Extracting ID and coordinates from document"""
        item_coordinates = [
            item['property_coordinates']['latitude'],
            item['property_coordinates']['longitude'],
        ]
        item_id = item['_id']
        log_id = str(item_id)
        print({'Starting processing': log_id})

        try:
            """Getting address"""
            get_address = geolocator.reverse(item_coordinates, language='en', addressdetails=True, zoom=18)

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
            print({datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"): log_id})

            """Cooldown to avoid throttling"""
            time.sleep(1)

        except:
            print('Problem with ' + log_id)

            """Cooldown to avoid throttling"""
            time.sleep(1)

    print('Work done')


if __name__ == "__main__":
    accurate_address()
