restart: down up

init: spain_property ireland

### Compose shortcuts
up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

sh:
	docker-compose run -p 5000:5000 --rm scraper_launch bash

logs:
	docker-compose logs -f

check:
	docker-compose ps && docker ps
# docker attach <container_id>

#
##
### Project shortcuts
celery:
	docker-compose run -d --rm scraper_launch celery -A root worker --beat --loglevel=info

ireland:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/ireland/ireland_daft_spider.py

bulgaria:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/bulgaria/bulgaria_imot_spider.py

malta:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/malta/malta_dardingli_spider.py

spain_fotocasa:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/spain/spain_fotocasa_spider.py

spain_idealista:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/spain_idealista_property_spider.py

spain_yaencontre:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/spain/spain_yaencontre_spider.py

italy:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/italy/italy_immobiliare_spider.py

france:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/france/france_immobilier_spider.py

greece:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/greece/greece_grekodom_spider.py

turkey:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/turkey/turkey_emlakjet_spider.py

croatia:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/croatia/croatia_croatiaestate_spider.py

accurate_address:
	docker-compose run -d --rm scraper_launch python src/webscraper/processing/addresses/accurate_address.py

convert_prices:
	docker-compose run -d --rm scraper_launch python src/webscraper/processing/prices/currency_convertation.py

update_prices:
	docker-compose run -d --rm scraper_launch python src/webscraper/processing/prices/actual_prices.py

thumbnail_main:
	docker-compose run -d --rm scraper_launch python src/webscraper/processing/images/thumbnail_main_image.py

#
##
### Project shortcuts for debugging
celery_test:
	docker-compose run --rm scraper_launch celery -A root worker --beat --loglevel=info

ireland_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/ireland/ireland_daft_spider.py

bulgaria_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/bulgaria/bulgaria_imot_spider.py

malta_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/malta/malta_dardingli_spider.py

spain_fotocasa_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/spain/spain_fotocasa_spider.py

spain_idealista_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/spain_idealista_property_spider.py

spain_yaencontre_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/spain/spain_yaencontre_spider.py

italy_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/italy/italy_immobiliare_spider.py

france_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/france/france_immobilier_spider.py

greece_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/greece/greece_grekodom_spider.py

turkey_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/turkey/turkey_emlakjet_spider.py

croatia_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/croatia/croatia_croatiaestate_spider.py

accurate_address_test:
	docker-compose run --rm scraper_launch python src/webscraper/processing/addresses/accurate_address.py

convert_prices_test:
	docker-compose run --rm scraper_launch python src/webscraper/processing/prices/currency_convertation.py

update_prices_test:
	docker-compose run --rm scraper_launch python src/webscraper/processing/prices/actual_prices.py

thumbnail_main_test:
	docker-compose run --rm scraper_launch python src/webscraper/processing/images/thumbnail_main_image.py

#
##
### Linters
