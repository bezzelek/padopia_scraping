"""Script that updates prices according to current currencies exchange rate"""

from webscraper.processing.prices.helpers import get_db_connection, get_exchange_rate, processing_documents


def update_prices():
    """DB connection"""
    db = get_db_connection()
    collection_property = db['property']

    """Search details"""
    query = {
        '$and': [
            {'property_price.price_last_update': {'$exists': True}},
            {'property_price.source.currency_iso': {'$ne': 'EUR'}},
        ]
    }
    sort = 'property_price.last_update', 1
    purpose_type = False

    """Getting number of properties without accurate address"""
    number_of_docs = collection_property.count_documents(query)

    """Log"""
    print(f'Work started! There are {number_of_docs} records to process...')

    """Getting currencies exchange rates"""
    exchange_rates = get_exchange_rate('EUR')

    """Processing documents"""
    result = processing_documents(query, number_of_docs, exchange_rates, sort, purpose_type)

    """Log"""
    print(f'Job done! {result} records processed of {number_of_docs}.')


if __name__ == "__main__":
    update_prices()
