import time
import json

import dns
import pymongo

from bson import ObjectId
from datetime import datetime
from bson.json_util import dumps

from pymongo import MongoClient
from currency_converter import CurrencyConverter

from src.webscraper.settings import DB_CONNECTION


def get_db_connection():
    """MongoDB client"""
    connection = MongoClient(DB_CONNECTION)
    db = connection['padopiadata']
    return db


def get_exchange_rate(target_currency):
    converter = CurrencyConverter()

    currencies = ['USD', 'BGN', 'TRY']
    exchange_rates = {'EUR': 1}
    for item in currencies:
        exchange_rate = converter.convert(1, item, target_currency)
        exchange_rates[item] = exchange_rate

        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'One {item} costs {exchange_rate} {target_currency}...'
        })

        """Preventing throttling"""
        time.sleep(0.5)

    return exchange_rates


def processing_documents(query, number_of_docs, exchange_rates, sort, purpose_type):
    """DB connection"""
    db = get_db_connection()
    collection_property = db['property']

    """Processed documents"""
    processed_documents = []

    for number in range(number_of_docs):
        """Log"""
        print(f'Starting to process record #{number} of {number_of_docs}...')

        """Getting document without currency ISO format"""
        if purpose_type:
            item_search = find_record_for_convert(collection_property, query, number)
        else:
            item_search = find_record_for_update(collection_property, query, number, sort)

        item = json.loads(dumps(item_search))
        item_len = len(item)

        """Extracting values from document"""
        if item_len != 0:
            item_id = item[0]['_id']['$oid']
            log_id = str(item_id)
            item_cost_amount = item[0]['property_cost_integer']
            item_cost_currency = item[0]['property_cost_currency']

        else:
            """Log"""
            print({
                datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                    f'ERROR while trying to extract record #{number} from database!'
            })
            item_cost_amount = None
            item_cost_currency = None

        """Converting currency symbol to ISO format"""
        currency_iso = currency_symbol_to_iso(log_id, item_cost_currency)

        """Converting source price to EUR"""
        price_in_eur = convert_price(log_id, item_cost_amount, currency_iso, exchange_rates)
        date_time = datetime.utcnow()

        """Updating database record"""
        updating_document(
            log_id, item_id, currency_iso, price_in_eur, item_cost_currency,
            item_cost_amount, date_time, collection_property
        )

        processed_documents.append(log_id)

    result = len(processed_documents)
    return result


def find_record_for_convert(collection_property, query, number):
    item_search = collection_property.find(query).skip(number).limit(1)
    return item_search


def find_record_for_update(collection_property, query, number, sort):
    item_search = collection_property.find(query).sort([sort]).skip(number).limit(1)
    return item_search


def currency_symbol_to_iso(log_id, source_currency):
    """Converting currency symbol to ISO format"""
    if source_currency is not None:
        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| Converting currency symbol to currency ISO format...'
        })

        currency_to_iso = (
            'EUR' if source_currency == '€'
            else 'USD' if source_currency == '$'
            else 'BGN' if source_currency == 'лв'
            else 'TRY' if source_currency == '₺'
            else None
        )

        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| Item currency is {currency_to_iso}...'
        })
        return currency_to_iso

    else:
        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR when converting currency symbol to ISO format! Source symbol is {source_currency}.'
        })
        return None


def convert_price(log_id, amount, in_currency, exchange_rates):
    try:
        source_amount = int(amount)
        exchange_rate = exchange_rates[in_currency]
        price = source_amount * exchange_rate
        result = round(price)

        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| Price converted. {source_amount} {in_currency} equals {result} EUR...'
        })

        return result

    except:
        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR while converting! Source currency is {in_currency}. Source price is {amount}.'
        })
        return None


def updating_document(
        log_id, item_id, currency_iso, amount, currency_symbol, amount_source, date_time, collection_property
):

    """Updating property document"""
    try:
        collection_property.update_one(
            {
                '_id': ObjectId(item_id)
            },
            {
                '$set':
                    {
                        'property_price.eur.amount': int(amount),
                        'property_price.eur.currency_iso': 'EUR',
                        'property_price.eur.currency_symbol': '€',
                        'property_price.source.amount': int(amount_source),
                        'property_price.source.currency_iso': str(currency_iso),
                        'property_price.source.currency_symbol': str(currency_symbol),
                        'property_price.price_last_update': date_time,
                    }
            }
        )

        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| Record updated successfully!'
        })

    except:
        """Log"""
        print({
            datetime.now().strftime("%d/%m/%Y ||| %H:%M:%S"):
                f'{log_id} ||| ERROR while trying to update record in database!'
        })
