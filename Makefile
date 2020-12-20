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

### Project shortcuts
celery:
	docker-compose run -d --rm scraper_launch celery -E -A root worker --beat --loglevel=info

spain_property:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/spain/spain_idealista_property_spider.py

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

italy:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/italy/italy_immobiliare_spider.py

france:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/france/france_immobilier_spider.py

greece:
	docker-compose run -d --rm scraper_launch python src/webscraper/spiders/greece/greece_grekodom_spider.py

### Project shortcuts for debugging
celery_test:
	docker-compose run --rm scraper_launch celery -E -A root worker --beat --loglevel=info

spain_property_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/spain/spain_idealista_property_spider.py

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

italy_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/italy/italy_immobiliare_spider.py

france_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/france/france_immobilier_spider.py

greece_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/greece/greece_grekodom_spider.py

### Linters
