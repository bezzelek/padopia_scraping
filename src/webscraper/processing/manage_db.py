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

    test = collection_property.update_many(
        {}, {"$unset": {"property_photo_thumbnail": 1}}
    )


if __name__ == "__main__":
    manage_db()
