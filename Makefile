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

### Project shortcuts
celery:
	docker-compose run --rm scraper_launch celery -E -A root worker --beat --loglevel=info

spain_property:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/spain/spain_idealista_property_spider.py

ireland:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/ireland/ireland_daft_spider.py

### Linters
