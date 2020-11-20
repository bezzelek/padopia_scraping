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

### Project shortcuts for debugging
celery_test:
	docker-compose run --rm scraper_launch celery -E -A root worker --beat --loglevel=info

spain_property_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/spain/spain_idealista_property_spider.py

ireland_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/ireland/ireland_daft_spider.py

bulgaria_test:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/bulgaria/bulgaria_imot_spider.py

### Linters
