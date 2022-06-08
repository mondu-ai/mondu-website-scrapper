# mondu-website-scrapper
This repository creates a website scrapper for gathering information and potentially helping us find leads.
## Structure

This repository is built with the help of Scrapy project structure
[Scrapy Create A Project](https://docs.scrapy.org/en/latest/intro/tutorial.html).

# mondu_website_scrapper

* [mondu_website_scrapper/](./mondu_website_scrapper/mondu_website_scrapper)
  * [scraped_results/](./mondu_website_scrapper/mondu_website_scrapper/scraped_results)
    * generalinformationitem.csv
    * priceitem.csv
  * [spiders/](./mondu_website_scrapper/mondu_website_scrapper/spiders)
    * [__init__.py](./mondu_website_scrapper/mondu_website_scrapper/spiders/__init__.py)
    * [catch_fish_scraper.py](./mondu_website_scrapper/mondu_website_scrapper/spiders/catch_fish_scraper.py)
  * [__init__.py](./mondu_website_scrapper/mondu_website_scrapper/__init__.py)
  * [export.py](./mondu_website_scrapper/mondu_website_scrapper/export.py)
  * [items.py](./mondu_website_scrapper/mondu_website_scrapper/items.py)
  * [middlewares.py](./mondu_website_scrapper/mondu_website_scrapper/middlewares.py)
  * [pipelines.py](./mondu_website_scrapper/mondu_website_scrapper/pipelines.py)
  * [settings.py](./mondu_website_scrapper/mondu_website_scrapper/settings.py)
  * [utils.py](./mondu_website_scrapper/mondu_website_scrapper/utils.py)
* [tests/](./mondu_website_scrapper/tests)
  * [utils.py/](./mondu_website_scrapper/tests/utils.py)
  * [__init__.py](./mondu_website_scrapper/tests/__init__.py)
* [.flake8](./mondu_website_scrapper/.flake8)
* [.gitignore](./mondu_website_scrapper/.gitignore)
* [.pylintrc](./mondu_website_scrapper/.pylintrc)
* [LICENSE](./mondu_website_scrapper/LICENSE)
* [Makefile](./mondu_website_scrapper/Makefile)
* [Pipfile](./mondu_website_scrapper/Pipfile)
* [Pipfile.lock](./mondu_website_scrapper/Pipfile.lock)
* [README.md](./mondu_website_scrapper/README.md)
* [pyproject.toml](./mondu_website_scrapper/pyproject.toml)
* [scrapy.cfg](./mondu_website_scrapper/scrapy.cfg)
* [setup.cfg](./mondu_website_scrapper/setup.cfg)
* [setup.py](./mondu_website_scrapper/setup.py)
