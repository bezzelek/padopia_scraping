# Scrapy settings for webscraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
"""Import for selenium"""
from shutil import which

BOT_NAME = 'webscraper'

SPIDER_MODULES = ['src.webscraper.spiders']
NEWSPIDER_MODULE = 'src.webscraper.spiders'

ROBOTSTXT_OBEY = False

"""DB settings"""
DB_CONNECTION = "mongodb+srv://padopiadbuser:WZHZbvqLq5kf4gDyHkzG@padopiacluster.p0hcr.mongodb.net/<dbname>?retryWrites=true&w=majority"
ITEM_PIPELINES = {
    'webscraper.pipelines.PropertyPipeline': 300,
}

# CONCURRENT_REQUESTS = 5
# DOWNLOAD_DELAY = 2

"""Middlewares for useragent, rotating proxies and selenium"""
# DOWNLOADER_MIDDLEWARES = {
#     'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
#     'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
#     'scrapy_selenium.SeleniumMiddleware': 800,
#     # 'rotating_proxies.middlewares.RotatingProxyMiddleware': 560,
#     # 'rotating_proxies.middlewares.BanDetectionMiddleware': 570,
# }


"""Selenium settings"""
# SELENIUM_DRIVER_NAME = 'chrome'
# SELENIUM_DRIVER_EXECUTABLE_PATH = which('chromedriver')
# SELENIUM_DRIVER_ARGUMENTS = ['--headless']  # '--headless' if using chrome instead of firefox

"""Base file layout"""
# ROTATING_PROXY_LIST_PATH = 'proxy.txt'
# ROTATING_PROXY_PAGE_RETRY_TIMES = 100
# ROTATING_PROXY_LOGSTATS_INTERVAL = 5
# ROTATING_PROXY_BACKOFF_BASE = 2
# ROTATING_PROXY_BACKOFF_CAP = 4
# 
# RANDOMIZE_DOWNLOAD_DELAY = True
# COOKIES_ENABLED = False
# # CONCURRENT_ITEMS = 200
# CONCURRENT_REQUESTS=50
# DOWNLOAD_DELAY= 0
# CONCURRENT_REQUESTS_PER_DOMAIN=50
# # LOG_LEVEL = 'ERROR'
# RETRY_TIMES = 2
# CONNECTION_TIMEOUT = 30

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'webscraper (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}


# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'webscraper.middlewares.WebscraperSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'webscraper.middlewares.WebscraperDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'webscraper.pipelines.WebscraperPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
