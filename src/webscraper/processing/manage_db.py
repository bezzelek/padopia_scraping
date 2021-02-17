from pymongo import MongoClient

from src.webscraper.settings import DB_CONNECTION


def manage_db():

    """Connecting to DB"""
    connection = MongoClient(DB_CONNECTION)
    db = connection['padopiadata']
    collection_property = db['test_property']

    """Manage DB"""
    # test = collection_property.update_many(
    #     {}, {"$unset": {"property_price": 1}}
    # )

    # test = collection_property.update_many(
    #     {}, {"$unset": {"property_photo_thumbnail": 1}}
    # )

    test = collection_property.aggregate([
            {
                '$search': {
                    'index': 'default',
                    'text': {
                        'query': 'Spain',
                        'path': [
                            'property_website_country',
                        ],
                    }
                }
            },

            # Return only 'property_address_detailed.country' field value and groups duplications
            {
                '$group':
                    {
                        '_id': '$property_type',
                    }
            },
        ])

    property_types_extract = []
    for item in test:
        property_type = item['_id']
        property_types_extract.append(property_type)

    print(property_types_extract)


if __name__ == "__main__":
    manage_db()
