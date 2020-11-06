restart: down up

init: scraper

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

scraper:
	docker-compose run --rm scraper_launch python src/webscraper/spiders/runner.py

### Linters
