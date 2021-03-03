from celery import Celery
from celery.schedules import crontab

from root.settings import BROKER_URL, CELERY_WORKERS
from webscraper.processing.addresses.accurate_address import accurate_address
from webscraper.processing.geospatial.mongo_geo import create_mongodb_geo_object
from webscraper.processing.images.thumbnail_main_image import make_thumbnails
from webscraper.processing.prices.actual_prices import update_prices
from webscraper.processing.prices.currency_convertation import convert_currency
from webscraper.spiders.bulgaria.bulgaria_imot_spider import BulgariaImotScraper
from webscraper.spiders.croatia.croatia_croatiaestate_spider import CroatiaCroatiaestateScraper
from webscraper.spiders.france.france_immobilier_spider import FranceImmobilierScraper
from webscraper.spiders.greece.greece_grekodom_spider import GreeceGrekodomScraper
from webscraper.spiders.ireland.ireland_daft_spider import IrelandDaftScraper
from webscraper.spiders.italy.italy_immobiliare_spider import ItalyImmobiliareScraper
from webscraper.spiders.malta.malta_dardingli_spider import MaltaDardingliScraper
from webscraper.spiders.spain.spain_fotocasa_spider import SpainFotocasaScraper
from webscraper.spiders.spain.spain_yaencontre_spider import SpainYaencontreScraper
from webscraper.spiders.spain_idealista_property_spider import SpainIdealistaPropertyScraper
from webscraper.spiders.turkey.turkey_emlakjet_spider import TurkeyEmlakjetScraper


app = Celery('celery', broker=BROKER_URL)

app.conf.update({
    'task_default_delivery_mode': 'transient',
    'broker_connection_timeout': 5.0,
    'broker_connection_max_retries': 12,
    'worker_concurrency': CELERY_WORKERS,
})


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=14, minute=50),
        run_mongodb_geo_object.s(),
        time_limit=60 * 60 * 23
    )

    sender.add_periodic_task(
        crontab(hour=14, minute=52),
        run_make_thumbnails.s(),
        time_limit=60 * 60 * 23
    )

    sender.add_periodic_task(
        crontab(hour=14, minute=54),
        run_convert_currency.s(),
        time_limit=60 * 60 * 23
    )

    sender.add_periodic_task(
        crontab(hour=14, minute=56),
        run_update_prices.s(),
        time_limit=60 * 60 * 23
    )

    sender.add_periodic_task(
        crontab(hour=14, minute=58),
        run_accurate_address.s(),
        time_limit=60 * 60 * 23
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=0, day_of_week='mon,wed,fri'),
        run_bulgaria_imot.s(),
        time_limit=60 * 60 * 47
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=2, day_of_week='mon,wed,fri'),
        run_croatia_croatiaestate.s(),
        time_limit=60 * 60 * 47
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=4, day_of_week='mon,wed,fri'),
        run_france_immobilier.s(),
        time_limit=60 * 60 * 47
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=6, day_of_week='mon,wed,fri'),
        run_greece_grekodom.s(),
        time_limit=60 * 60 * 47
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=8, day_of_week='mon,wed,fri'),
        run_ireland_daft.s(),
        time_limit=60 * 60 * 47
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=10, day_of_week='mon,wed,fri'),
        run_italy_immobiliare.s(),
        time_limit=60 * 60 * 47
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=12, day_of_week='mon,wed,fri'),
        run_malta_dardingli.s(),
        time_limit=60 * 60 * 47
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=14, day_of_week='mon,wed,fri'),
        run_turkey_emlakjet.s(),
        time_limit=60 * 60 * 47
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=16, day_of_week='mon,wed,fri'),
        run_spain_yaencontre.s(),
        time_limit=60 * 60 * 47
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=18, day_of_week='mon,wed,fri'),
        run_spain_fotocasa.s(),
        time_limit=60 * 60 * 47
    )

    sender.add_periodic_task(
        crontab(hour=15, minute=20, day_of_week='mon,wed,fri'),
        run_spain_idealista.s(),
        time_limit=60 * 60 * 47
    )


@app.task
def run_accurate_address():
    accurate_address()


@app.task
def run_convert_currency():
    convert_currency()


@app.task
def run_update_prices():
    update_prices()


@app.task
def run_make_thumbnails():
    make_thumbnails()


@app.task
def run_mongodb_geo_object():
    create_mongodb_geo_object()


@app.task
def run_bulgaria_imot():
    scraper = BulgariaImotScraper()
    scraper.run_spiders()


@app.task
def run_croatia_croatiaestate():
    scraper = CroatiaCroatiaestateScraper()
    scraper.run_spiders()


@app.task
def run_france_immobilier():
    scraper = FranceImmobilierScraper()
    scraper.run_spiders()


@app.task
def run_greece_grekodom():
    scraper = GreeceGrekodomScraper()
    scraper.run_spiders()


@app.task
def run_ireland_daft():
    scraper = IrelandDaftScraper()
    scraper.run_spiders()


@app.task
def run_italy_immobiliare():
    scraper = ItalyImmobiliareScraper()
    scraper.run_spiders()


@app.task
def run_malta_dardingli():
    scraper = MaltaDardingliScraper()
    scraper.run_spiders()


@app.task
def run_turkey_emlakjet():
    scraper = TurkeyEmlakjetScraper()
    scraper.run_spiders()


@app.task
def run_spain_fotocasa():
    scraper = SpainFotocasaScraper()
    scraper.run_spiders()


@app.task
def run_spain_idealista():
    scraper = SpainIdealistaPropertyScraper()
    scraper.run_spiders()


@app.task
def run_spain_yaencontre():
    scraper = SpainYaencontreScraper()
    scraper.run_spiders()
