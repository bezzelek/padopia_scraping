from celery.schedules import crontab
from celery.task import periodic_task

from webscraper.spiders.bulgaria.bulgaria_imot_spider import BulgariaImotScraper
from webscraper.spiders.croatia.croatia_croatiaestate_spider import CroatiaCroatiaestateScraper
from webscraper.spiders.france.france_immobilier_spider import FranceImmobilierScraper
from webscraper.spiders.greece.greece_grekodom_spider import GreeceGrekodomScraper
from webscraper.spiders.ireland.ireland_daft_spider import IrelandDaftScraper
from webscraper.spiders.italy.italy_immobiliare_spider import ItalyImmobiliareScraper
from webscraper.spiders.malta.malta_dardingli_spider import MaltaDardingliScraper
from webscraper.spiders.spain.spain_fotocasa_spider import SpainFotocasaScraper
from webscraper.spiders.spain.spain_idealista_alava_spider import SpainIdealistaAlavaScraper
from webscraper.spiders.spain.spain_idealista_albacete_spider import SpainIdealistaAlbaceteScraper
from webscraper.spiders.spain.spain_idealista_alicante_spider import SpainIdealistaAlicanteScraper
from webscraper.spiders.spain.spain_idealista_almeria_spider import SpainIdealistaAlmeriaScraper
from webscraper.spiders.spain.spain_idealista_andorra_spider import SpainIdealistaAndorraScraper
from webscraper.spiders.spain.spain_idealista_asturias_spider import SpainIdealistaAsturiasScraper
from webscraper.spiders.spain.spain_idealista_avila_spider import SpainIdealistaAvilaScraper
from webscraper.spiders.spain.spain_idealista_badajoz_spider import SpainIdealistaBadajozScraper
from webscraper.spiders.spain.spain_idealista_balears_spider import SpainIdealistaBalearicScraper
from webscraper.spiders.spain.spain_idealista_barcelona_spider import SpainIdealistaBarcelonaScraper
from webscraper.spiders.spain.spain_idealista_burgos_spider import SpainIdealistaBurgosScraper
from webscraper.spiders.spain.spain_idealista_caceres_spider import SpainIdealistaCaceresScraper
from webscraper.spiders.spain.spain_idealista_cadiz_spider import SpainIdealistaCadizScraper
from webscraper.spiders.spain.spain_idealista_cantabria_spider import SpainIdealistaCantabriaScraper
from webscraper.spiders.spain.spain_idealista_castellon_spider import SpainIdealistaCastellonScraper
from webscraper.spiders.spain.spain_idealista_cerdanya_spider import SpainIdealistaCerdanyaScraper
from webscraper.spiders.spain.spain_idealista_ceuta_spider import SpainIdealistaCeutaScraper
from webscraper.spiders.spain.spain_idealista_ciudad_spider import SpainIdealistaCiudadScraper
from webscraper.spiders.spain.spain_idealista_cordoba_spider import SpainIdealistaCordobaScraper
from webscraper.spiders.spain.spain_idealista_coruna_spider import SpainIdealistaCorunaScraper
from webscraper.spiders.spain.spain_idealista_cuenca_spider import SpainIdealistaCuencaScraper
from webscraper.spiders.spain.spain_idealista_girona_spider import SpainIdealistaGeronaScraper
from webscraper.spiders.spain.spain_idealista_granada_spider import SpainIdealistaGranadaScraper
from webscraper.spiders.spain.spain_idealista_guadalajara_spider import SpainIdealistaGuadalajaraScraper
from webscraper.spiders.spain.spain_idealista_guipuzcoa_spider import SpainIdealistaGipuzkoaScraper
from webscraper.spiders.spain.spain_idealista_huelva_spider import SpainIdealistaHuelvaScraper
from webscraper.spiders.spain.spain_idealista_huesca_spider import SpainIdealistaHuescaScraper
from webscraper.spiders.spain.spain_idealista_jaen_spider import SpainIdealistaJaenScraper
from webscraper.spiders.spain.spain_idealista_leon_spider import SpainIdealistaLeonScraper
from webscraper.spiders.spain.spain_idealista_lleida_spider import SpainIdealistaLleidaScraper
from webscraper.spiders.spain.spain_idealista_lugo_spider import SpainIdealistaLugoScraper
from webscraper.spiders.spain.spain_idealista_madrid_spider import SpainIdealistaMadridScraper
from webscraper.spiders.spain.spain_idealista_malaga_spider import SpainIdealistaMalagaScraper
from webscraper.spiders.spain.spain_idealista_melilla_spider import SpainIdealistaMelillaScraper
from webscraper.spiders.spain.spain_idealista_murcia_spider import SpainIdealistaMurciaScraper
from webscraper.spiders.spain.spain_idealista_navarra_spider import SpainIdealistaNavarraScraper
from webscraper.spiders.spain.spain_idealista_ourense_spider import SpainIdealistaOurenseScraper
from webscraper.spiders.spain.spain_idealista_pais_spider import SpainIdealistaPaisScraper
from webscraper.spiders.spain.spain_idealista_palencia_spider import SpainIdealistaPalenciaScraper
from webscraper.spiders.spain.spain_idealista_palmas_spider import SpainIdealistaPalmasScraper
from webscraper.spiders.spain.spain_idealista_pontevedra_spider import SpainIdealistaPontevedraScraper
from webscraper.spiders.spain.spain_idealista_rioja_spider import SpainIdealistaRiojaScraper
from webscraper.spiders.spain.spain_idealista_salamanca_spider import SpainIdealistaSalamancaScraper
from webscraper.spiders.spain.spain_idealista_segovia_spider import SpainIdealistaSegoviaScraper
from webscraper.spiders.spain.spain_idealista_sevilla_spider import SpainIdealistaSevilleScraper
from webscraper.spiders.spain.spain_idealista_soria_spider import SpainIdealistaSoriaScraper
from webscraper.spiders.spain.spain_idealista_tarragona_spider import SpainIdealistaTarragonaScraper
from webscraper.spiders.spain.spain_idealista_tenerife_spider import SpainIdealistaTenerifeScraper
from webscraper.spiders.spain.spain_idealista_teruel_spider import SpainIdealistaTeruelScraper
from webscraper.spiders.spain.spain_idealista_toledo_spider import SpainIdealistaToledoScraper
from webscraper.spiders.spain.spain_idealista_valencia_spider import SpainIdealistaValenciaScraper
from webscraper.spiders.spain.spain_idealista_valladolid_spider import SpainIdealistaValladolidScraper
from webscraper.spiders.spain.spain_idealista_vizcaya_spider import SpainIdealistaBiscayScraper
from webscraper.spiders.spain.spain_idealista_zamora_spider import SpainIdealistaZamoraScraper
from webscraper.spiders.spain.spain_idealista_zaragoza_spider import SpainIdealistaZaragozaScraper
from webscraper.spiders.spain_idealista_property_spider import SpainIdealistaPropertyScraper
from webscraper.spiders.turkey.turkey_emlakjet_spider import TurkeyEmlakjetScraper


@periodic_task(run_every=crontab(hour=0, minute=5, day_of_week='mon,tue,wed,thu,fri,sun,sat'), time_limit=60 * 60 * 23)
def run_ireland_daft():
    scraper = IrelandDaftScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=1, minute=5, day_of_week='mon,tue,wed,thu,fri,sun,sat'), time_limit=60 * 60 * 23)
def run_italy_immobiliare():
    scraper = ItalyImmobiliareScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=2, minute=5, day_of_week='mon,tue,wed,thu,fri,sun,sat'), time_limit=60 * 60 * 23)
def run_turkey_emlakjet():
    scraper = TurkeyEmlakjetScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=6, minute=5, day_of_week='mon,tue,wed,thu,fri,sun,sat'), time_limit=60 * 60 * 23)
def run_malta_dardingli():
    scraper = MaltaDardingliScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=7, minute=5, day_of_week='mon,tue,wed,thu,fri,sun,sat'), time_limit=60 * 60 * 23)
def run_france_immobilier():
    scraper = FranceImmobilierScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=8, minute=5, day_of_week='mon,tue,wed,thu,fri,sun,sat'), time_limit=60 * 60 * 23)
def run_croatia_croatiaestate():
    scraper = CroatiaCroatiaestateScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=12, minute=5, day_of_week='mon,tue,wed,thu,fri,sun,sat'), time_limit=60 * 60 * 23)
def run_bulgaria_imot():
    scraper = BulgariaImotScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=13, minute=5, day_of_week='mon,tue,wed,thu,fri,sun,sat'), time_limit=60 * 60 * 23)
def run_greece_grekodom():
    scraper = GreeceGrekodomScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=18, minute=5, day_of_week='mon,tue,wed,thu,fri,sun,sat'), time_limit=60 * 60 * 23)
def run_spain_fotocasa():
    scraper = SpainFotocasaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=19, minute=5, day_of_week='mon,tue,wed,thu,fri,sun,sat'), time_limit=60 * 60 * 23)
def run_spain_idealista():
    scraper = SpainIdealistaPropertyScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=0, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_alava():
    scraper = SpainIdealistaAlavaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=0, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_albacete():
    scraper = SpainIdealistaAlbaceteScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=0, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_alicante():
    scraper = SpainIdealistaAlicanteScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=1, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_almeria():
    scraper = SpainIdealistaAlmeriaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=1, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_andorra():
    scraper = SpainIdealistaAndorraScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=1, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_asturias():
    scraper = SpainIdealistaAsturiasScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=2, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_avila():
    scraper = SpainIdealistaAvilaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=2, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_badajoz():
    scraper = SpainIdealistaBadajozScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=2, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_balears():
    scraper = SpainIdealistaBalearicScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=3, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_barcelona():
    scraper = SpainIdealistaBarcelonaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=3, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_burgos():
    scraper = SpainIdealistaBurgosScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=3, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_caceres():
    scraper = SpainIdealistaCaceresScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=4, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_cadiz():
    scraper = SpainIdealistaCadizScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=4, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_cantabria():
    scraper = SpainIdealistaCantabriaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=4, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_castellon():
    scraper = SpainIdealistaCastellonScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=5, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_cerdanya():
    scraper = SpainIdealistaCerdanyaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=5, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_ceuta():
    scraper = SpainIdealistaCeutaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=5, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_ciudad():
    scraper = SpainIdealistaCiudadScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=6, minute=00, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_cordoba():
    scraper = SpainIdealistaCordobaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=6, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_coruna():
    scraper = SpainIdealistaCorunaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=6, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_cuenca():
    scraper = SpainIdealistaCuencaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=7, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_girona():
    scraper = SpainIdealistaGeronaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=7, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_granada():
    scraper = SpainIdealistaGranadaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=7, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_guadalajara():
    scraper = SpainIdealistaGuadalajaraScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=8, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_guipuzcoa():
    scraper = SpainIdealistaGipuzkoaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=8, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_huelva():
    scraper = SpainIdealistaHuelvaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=8, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_huesca():
    scraper = SpainIdealistaHuescaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=9, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_jaen():
    scraper = SpainIdealistaJaenScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=9, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_leon():
    scraper = SpainIdealistaLeonScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=9, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_lleida():
    scraper = SpainIdealistaLleidaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=10, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_lugo():
    scraper = SpainIdealistaLugoScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=10, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_madrid():
    scraper = SpainIdealistaMadridScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=10, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_malaga():
    scraper = SpainIdealistaMalagaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=11, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_melilla():
    scraper = SpainIdealistaMelillaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=11, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_murcia():
    scraper = SpainIdealistaMurciaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=11, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_navarra():
    scraper = SpainIdealistaNavarraScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=12, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_ourense():
    scraper = SpainIdealistaOurenseScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=12, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_pais():
    scraper = SpainIdealistaPaisScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=12, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_palencia():
    scraper = SpainIdealistaPalenciaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=13, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_palmas():
    scraper = SpainIdealistaPalmasScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=13, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_pontevedra():
    scraper = SpainIdealistaPontevedraScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=13, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_rioja():
    scraper = SpainIdealistaRiojaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=14, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_salamanca():
    scraper = SpainIdealistaSalamancaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=14, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_segovia():
    scraper = SpainIdealistaSegoviaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=14, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_sevilla():
    scraper = SpainIdealistaSevilleScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=15, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_soria():
    scraper = SpainIdealistaSoriaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=15, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_tarragona():
    scraper = SpainIdealistaTarragonaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=15, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_tenerife():
    scraper = SpainIdealistaTenerifeScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=16, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_teruel():
    scraper = SpainIdealistaTeruelScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=16, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_toledo():
    scraper = SpainIdealistaToledoScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=16, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_valencia():
    scraper = SpainIdealistaValenciaScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=17, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_valladolid():
    scraper = SpainIdealistaValladolidScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=17, minute=20, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_vizcaya():
    scraper = SpainIdealistaBiscayScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=17, minute=40, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_zamora():
    scraper = SpainIdealistaZamoraScraper()
    scraper.run_spiders()


@periodic_task(run_every=crontab(hour=18, minute=0, day_of_week='sat,mon,wed'), time_limit=60 * 60 * 23 * 2)
def run_spain_idealista_zaragoza():
    scraper = SpainIdealistaZaragozaScraper()
    scraper.run_spiders()
