"""Scrapy settings for mondu_website_scrapper project"""
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from pathlib import Path

BOT_NAME = "mondu_website_scrapper"

SPIDER_MODULES = ["mondu_website_scrapper.spiders"]
NEWSPIDER_MODULE = "mondu_website_scrapper.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'mondu_website_scrapper (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'mondu_website_scrapper.middlewares.MonduWebsiteScrapperSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'mondu_website_scrapper.middlewares.MonduWebsiteScrapperDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "mondu_website_scrapper.pipelines.MonduWebsiteScrapperPipeline": 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings pylint: disable=line-too-long
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# Argument Set Up

# start urls input
START_URLS = [
    "https://www.microsoft.com/de-at",
    "https://www.giesswein.com/",
    "https://www.heimwerkertools.com/b2b",
    "https://www.atombody.at/",
    "https://www.eposcomputer.com/epos-business-center/",
    "https://gesa.at/en/",
    "https://www.flyeralarm.com/de/",
    "https://www.muenzeoesterreich.at/",
    "https://www.fischersports.com/at_en",
    "https://shop.mcshark.at/zubehoer",
    "https://jysk.at/",
]

# column name of urls given from gsheet
INPUT_URL_COLUMN_NAME = "company_url_cleaned"

# file folder for scraped results
FILE_FOLDER = Path.cwd().parent / "scraped_results"


# webshop searching keywords
WEBSHOP_KEYWORDS = [
    "warenkorb",
    "einkaufswagen",
    "jetzt bezahlen",
    "zahlungsmethoden",
    "zahlungsarten",
    "cart",
    "basket",
    "checkout",
    "pay now",
    "payment methods",
]

# payment methods searching keywords
PAYMENTS_KEYWORDS = [
    "mastercard",
    "visa",
    "paypal",
    "klarna",
    "sepa",
    "sofort",
    "apple",
    "amazon",
    "afterpay",
]

# b2b searching keywords
B2B_KEYWORDS = [
    "gro??kunde",
    "gesch??ftskunde",
    "gesch??ftskunden",
    "groh??ndler",
    "gro??handel",
    "gesch??ftskunden",
    "gewerbliche kunden",
    "wholesale",
    "b2b",
    "b-to-b",
    "reseller",
    "business customer",
    "business",
    "trade account",
    "trade-account",
    "companies",
    "institutions",
]

# websystem searching keywords
WEBSYSTEMS_KEYWORDS = [
    "Magento",
    "Magento 1",
    "Magento 2",
    "WooCommerce",
    "Shopware",
    "Shopware 5",
    "Shopware 6",
    "BigCommerce",
    "ePages",
    "JTL Shop",
    "JTL Shop 4",
    "JTL Shop 5",
    "Oxid",
    "Spryker",
    "commercetools",
    "SAP Commerce Cloud",
    "plentymarkets",
]

# currency sign
CURRENCY_SIGN = "$|EUR|???|GBP|??"

# price searching pattern
PRICE_PATTERN = (
    r"\d*[\.\,]?\d+(?=\s?[$|EUR|???|GBP|??])|(?<=[$|EUR|???|GBP|??])\s?\d*[\.\,]?\d+"
)

# searching phone pattern
# TODO write tests for it
PHONE_PATTERN = r"(?:\B\+ ?43|\+49)(?: *[(-]? *\d(?:[ \d]*\d)?)? *(?:[)-] *)?\d+ *(?:[/)-] *)?\d+ *(?:[/)-] *)?\d+(?: *- *\d+)?"  # pylint: disable=line-too-long

# searching email pattern
EMAIL_PATTERN = r"[\w.+-]+@[\w-]+\.[\w.-]+"
