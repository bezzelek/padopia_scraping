import os
import json
import asyncio
import aiohttp

import dns
import pymongo

from io import BytesIO
from datetime import datetime

from bson import ObjectId
from bson.json_util import dumps

from PIL import Image
from pymongo import MongoClient
from google.cloud import storage

from src.webscraper.settings import DB_CONNECTION


def start_client_storage():
    """Google client"""
    os.environ[
        'GOOGLE_APPLICATION_CREDENTIALS'
    ] = 'src/resonant-forge-294511-25f7c1fc6d0f.json'
    client = storage.Client()

    return client


def get_db_connection():
    """MongoDB client"""
    connection = MongoClient(DB_CONNECTION)
    db = connection['padopiadata']
    return db


def make_thumbnails():
    """Connecting to DB"""
    db = get_db_connection()
    collection_property = db['property']

    """Getting number of properties without thumbnail images"""
    number_of_docs = collection_property.count_documents({
        '$and': [
            {'property_photo': {'$exists': True}},
            {'property_photo_thumbnail': {'$exists': False}}
        ]
    })

    """Log"""
    print(f'Work started! There are {number_of_docs} records to process...')

    processed_documents = []
    for number in range(number_of_docs):
        """Extracting document to make thumbnail"""
        document = extract_document_to_process(number, number_of_docs, collection_property)

        """Extracting image details"""
        image_details = extract_image_details(document['item'], document['item_len'], number)

        """Converting image to thumbnail and saving it to GCP bucket"""
        processed_documents.append(image_details['log_id'])
        get_thumbnail = processing_image(image_details['item_photo'], image_details['log_id'])

        """Saving thumbnail image link to document"""
        update_db_record(get_thumbnail, collection_property, image_details['item_id'], image_details['log_id'])

    processed_documents_count = len(processed_documents)
    print(
        f'Job done! {processed_documents_count} records processed of {number_of_docs}.'
    )


def extract_document_to_process(number, number_of_docs, collection_property):
    """Log"""
    print(f'Starting to process record #{number} of {number_of_docs}...')

    """Getting document without accurate address"""
    item_search = collection_property.find({
        '$and': [
            {'property_photo': {'$exists': True}},
            {'property_images': {'$exists': False}}
        ]
    }).skip(number).limit(1)

    """Extracting ID and photos"""
    item = json.loads(dumps(item_search))
    item_len = len(item)

    result = {
        'item': item,
        'item_len': item_len,
    }

    return result


def extract_image_details(item, item_len, number):
    if item_len != 0:
        item_id = item[0]['_id']['$oid']
        log_id = str(item_id)

        item_photo = item[0]['property_photo']

        result = {
            'item_id': item_id,
            'log_id': log_id,
            'item_photo': item_photo,
        }
        return result

    else:
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'ERROR while trying to extract record #{number} from database!'
        })
        result = {
            'item_id': None,
            'log_id': None,
            'item_photo': None,
        }
        return result


def processing_image(item_photo, log_id):
    """Getting thumbnail image"""
    if item_photo is not None:

        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| Getting thumbnail image and transferring it to GCP Bucket...'
        })
        get_thumbnail = store_images(item_photo)[0]

        return get_thumbnail

    else:
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR because "item_photo" is {item_photo}!'
        })
        return None


def update_db_record(get_thumbnail, collection_property, item_id, log_id):
    """Updating property document"""
    if get_thumbnail is not None:
        collection_property.update_one(
            {
                '_id': ObjectId(item_id)
            },
            {
                '$set':
                    {
                        'property_images': {'main_photo': {'small': get_thumbnail}},
                    }
            }
        )

        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| Record updated successfully!'
        })
    else:
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR because thumbnail image is {get_thumbnail}!'
        })


def store_images(photos_list):
    loop = asyncio.get_event_loop()
    stored_links = loop.run_until_complete(create_tasks(photos_list))
    return stored_links


async def create_tasks(photos_list):
    urls = photos_list
    tasks = []
    async with aiohttp.ClientSession() as session:
        if type(urls) == list:
            for url in urls:
                task = asyncio.create_task(get_data(url, session))
                tasks.append(task)
        else:
            task = asyncio.create_task(get_data(urls, session))
            tasks.append(task)
        await asyncio.gather(*tasks)
    result = [item._result for item in tasks]
    return result


async def get_data(url, session):
    async with session.get(url) as response:

        """Extracting image and image data"""
        file = await response.read()
        file_name_get = os.path.split(url)
        file_name_pref = '320x240'
        file_name_suf = os.path.basename(file_name_get[1]).split('.')[0]
        file_name = file_name_pref + '_' + file_name_suf + '.jpeg'

        """Converting image to smaller size"""
        try:
            temp_file = BytesIO()
            open_file = Image.open(BytesIO(file))
            open_file.thumbnail((320, 240))
            open_file.save(temp_file, format="JPEG")
            temp_file.seek(0)
            file_bytes = temp_file.read()

            """Transferring to db"""
            tasks = []
            task = asyncio.create_task(transfer_to_db(file_bytes, file_name))
            tasks.append(task)
            await asyncio.gather(*tasks)
            for item in tasks:
                result = item._result
            return result
        except:
            return None


async def transfer_to_db(file, file_name):
    """Storing image to database"""
    client = start_client_storage()

    bucket_name = 'padopia-media-files'
    blob_name = 'photos/thumbnails/'
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name + file_name)
    check = storage.Blob(bucket=bucket, name=blob_name + file_name).exists(client=client)
    if check is True:
        result = blob.public_url
    else:
        blob.upload_from_string(file, content_type='image')
        blob.make_public()
        result = blob.public_url
    return result


if __name__ == "__main__":
    make_thumbnails()
