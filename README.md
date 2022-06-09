# mondu-website-scrapper

## Overview
This repository creates a website scraper for gathering information and hopefully helping us find high quality leads. For details, please read the documentation [Mondu Web Scraper - MVP
](https://mondu.atlassian.net/wiki/spaces/D/pages/27132335/Mondu+Web+Scraper+-+MVP) here. 
## Structure
### Project Structure

This repository is built with the help of Scrapy project structure
[Scrapy Create A Project](https://docs.scrapy.org/en/latest/intro/tutorial.html).

### mondu_website_scrapper

# mondu_website_scrapper
* [images/](./mondu_website_scrapper/images)
  * [Architecture_of_Scraper.drawio.png](./mondu_website_scrapper/images/Architecture_of_Scraper.drawio.png)
  * [google_sheet.png](./mondu_website_scrapper/images/google_sheet.png)
  * [google_sheet_export.png](./mondu_website_scrapper/images/google_sheet_export.png)
* [mondu_website_scrapper/](./mondu_website_scrapper/mondu_website_scrapper)
  * [gsheet_api/](./mondu_website_scrapper/mondu_website_scrapper/gsheet_api)
    * [__init__.py](./mondu_website_scrapper/mondu_website_scrapper/gsheet_api/__init__.py)
    * [client_secret.json](./mondu_website_scrapper/mondu_website_scrapper/gsheet_api/client_secret.json)
    * [export2_gsheet.py](./mondu_website_scrapper/mondu_website_scrapper/gsheet_api/export2_gsheet.py)
    * [gsheet_settings.py](./mondu_website_scrapper/mondu_website_scrapper/gsheet_api/gsheet_settings.py)
    * [read_from_gsheet.py](./mondu_website_scrapper/mondu_website_scrapper/gsheet_api/read_from_gsheet.py)
    * [utils.py](./mondu_website_scrapper/mondu_website_scrapper/gsheet_api/utils.py)
  * [scraped_results/](./mondu_website_scrapper/mondu_website_scrapper/scraped_results)
    * [findingnemo__report.csv](./mondu_website_scrapper/mondu_website_scrapper/scraped_results/findingnemo__report.csv)
    * [generalinformationitem.csv](./mondu_website_scrapper/mondu_website_scrapper/scraped_results/generalinformationitem.csv)
    * [priceitem.csv](./mondu_website_scrapper/mondu_website_scrapper/scraped_results/priceitem.csv)
  * [spiders/](./mondu_website_scrapper/mondu_website_scrapper/spiders)
    * [__init__.py](./mondu_website_scrapper/mondu_website_scrapper/spiders/__init__.py)
    * [catch_fish_scraper.py](./mondu_website_scrapper/mondu_website_scrapper/spiders/catch_fish_scraper.py)
  * [.env](./mondu_website_scrapper/mondu_website_scrapper/.env)
  * [.env.template](./mondu_website_scrapper/mondu_website_scrapper/.env.template)
  * [__init__.py](./mondu_website_scrapper/mondu_website_scrapper/__init__.py)
  * [export.py](./mondu_website_scrapper/mondu_website_scrapper/export.py)
  * [items.py](./mondu_website_scrapper/mondu_website_scrapper/items.py)
  * [middlewares.py](./mondu_website_scrapper/mondu_website_scrapper/middlewares.py)
  * [pipelines.py](./mondu_website_scrapper/mondu_website_scrapper/pipelines.py)
  * [settings.py](./mondu_website_scrapper/mondu_website_scrapper/settings.py)
  * [utils.py](./mondu_website_scrapper/mondu_website_scrapper/utils.py)
* [scraped_results/](./mondu_website_scrapper/scraped_results)
  * [findingnemo__report.csv](./mondu_website_scrapper/scraped_results/findingnemo__report.csv)
  * [generalinformationitem.csv](./mondu_website_scrapper/scraped_results/generalinformationitem.csv)
  * [priceitem.csv](./mondu_website_scrapper/scraped_results/priceitem.csv)
* [tests/](./mondu_website_scrapper/tests)
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


### Logic Structure
The main logic for this project is twofold:
1. **Build a spider for website scraping**: we have taken the great advantage of the Python Library Scrapy for website scraping. In quick summary, we have defined three main objects as followed:
    * [items.py](./mondu_website_scrapper/items.py): this file is created as an empty file when a scrapy project is created. The item objects are defined as key-value pairs and very much like a Python dictionary. Our scraped results will be saved under item objects.
    * [pipelines.py](./mondu_website_scrapper/pipelines.py): this file is created as an empty file when a scrapy project is created. The pipeline object takes items and processes items. For this particular project, we have processed items and then export them as csv files under the folder [scraped_results/](./mondu_website_scrapper/scraped_results).
    * [settings.py](./mondu_website_scrapper/settings.py): this file is created as an empty file when a scrapy project is created. All the searching patterns of our Scraper are defined under this file.
    * [catch_fish_scraper.py](./mondu_website_scrapper/spiders/catch_fish_scraper.py): this file creates the Spider class LeadSpider. It is inherited from a basic scrapy.spider. Notice that this script not only scraped data, but also cleaned data and generated the final report. We therefore have provided a flag `--use-cache` in the command line. Please check (#use-the-scraper) for more details.

For more details of Scrapy, I strongly recommend start from their official documentation [Scrapy 2.6 Documentation](https://docs.scrapy.org/en/latest/index.html).

1. **Wrangle and export scraping results to a Gsheet**: As how LeadSpider searched and scrapped websites are clearly explained under the documentation Mondu Web Scraper - MVP, we will not dive any deeper here. The main steps for exporting scraping results are:
  * Create a mondu website scraper project under the Mondu organization in Google cloud.
  * Enable Google Drive API and Google Sheet API for this project.
  * Create and download the client credential file.
  * The [gsheet_api/utils.py](./mondu_website_scrapper/gsheet_api/utils.py) file contains functions to get Gsheet credentials, create API client, create gsheet and worksheet etc.
  * [gsheet_settings.py](./mondu_website_scrapper/gsheet_api/gsheet_settings.py) defines the target gsheet where we want to export data to, gsheet scopes etc.
  * [client_secret.json](./mondu_website_scrapper/gsheet_api/client_secret.json) The client secret json file is the credential of Google Drive API of the gsheet. The secret GSHEET_PRIVATE_KEY_ID and GSHEET_PRIVATE_KEY are `null` at the moment. It will be shared by one password for people who will use this project.
  * [export2_gsheet.py](./mondu_website_scrapper/gsheet_api/export2_gsheet.py) handles the exporting. We export the report file to the pre-defined gsheet.
  *  [read_from_gsheet.py](./mondu_website_scrapper/gsheet_api/read_from_gsheet.py) handles the importing from the gsheet to a pandas dataframe.
## The Main Architecture 
![Alt text](/images/Architecture_of_Scraper.drawio.png?raw=true "Architecture_of_Scraper")

Shortly speaking, our web scraper will scrapy any  website by given URL, and create two items saved as `generalinformationitem.csv` and `priceitem.csv` file under `mondu_website_scrapper/scraped_results`. The scraped data will be cleaned and engineered, followed by creating the final report file `findingnemo.csv` under the same folder.

## Development
### Coding standards

We use the following packages for formatting and linting:

* `isort` sorts imports alphabetically, automatically separating them into sections by import type
* `black` auto-formats the code to ensure homogeneity and PEP8 compliance. Install instructions:
  [Visual Studio](https://dev.to/adamlombard/how-to-use-the-black-python-code-formatter-in-vscode-3lo0)
* `pylint` is a static code analysis tool, combined with code best practices. Note that it only
  highlights issues, but does not automatically solve them. Install instructions:
  [Visual Studio](https://code.visualstudio.com/docs/python/linting)

### Create dev environment
* We will be using Python 3.10 for this project
```bash
pyenv local 3.10.3
```
* Gsheet API credentials are shared through one password. Copy the .env.template file to .env and fill the credentials.
```bash
cp .env.template .env
```
* Start building your environment by using Pipfile. We will install both develop and default packages from Pipfile.
```bash
pipenv install --dev
```
* Active environment
```bash
pipenv shell
```
## Use the Scraper
The only input argument required for this scraper is an arbitrary URL. We have provided three ways to pass the argument to the scraper:
### Input Arguments
1. Passing an URL from [mondu_website_scrapper/settings.py](./mondu_website_scrapper/settings.py). Please add your URLs under the list `START_URLS`, for instance:
```python
START_URLS = [
    "https://www.szabo-scandic.com/",
    "https://b2b.vitrasan.com/",
    "https://www.hilti.at/",
    "https://shop.bibus.at/customer/account/create/",
    "https://b2b.accushop.at/",
    "https://b2b.akku-maeser.at/",
]
```
and in the main project folder `mondu_website_scrapper/mondu_website_scrapper`, run the following:
```python
pipenv run python spiders/catch_fish_scraper.py --no-use-cache --no-use-gsheet
```
for scraping every URL and creating a `findingnemo__report.csv` file under `scraped_results/` folder.
If you don't want re-scrapy the website, but just create a report by using existing `generalinformationitem.csv` and `priceitem.csv` files, please run:
```python
pipenv run python spiders/catch_fish_scraper.py --use-cache --no-use-gsheet
```

2. Passing an URL from the Gsheet. The specific Gsheet we have created and enabled Google Drive API is [Mondu-Web-Scraper-Data-Import-Export](https://docs.google.com/spreadsheets/d/1G8iNI0tBGOhRBhkPPJFKtqwtDjBi-ENHw3rYLQh0iyM/edit#gid=449735522). So far, everyone in the Mondu Orgnazation should have the access to this sheet. Please append your URL in the worksheet `Marketing-Input-Data` under the column `company_url`.
![Alt text](/images/google_sheet.png?raw=true "Mondu-Web-Scraper-Gsheet")
Then in the main project folder `mondu_website_scrapper/mondu_website_scrapper`, run the following:
```python
pipenv run python spiders/catch_fish_scraper.py --no-use-cache --use-gsheet
```
for scraping every URL and creating a `findingnemo__report.csv` file under `scraped_results/` folder.
If you don't want re-scrapy the website, but just create a report by using existing `generalinformationitem.csv` and `priceitem.csv` files, please run:
```python
pipenv run python spiders/catch_fish_scraper.py --use-cache --use-gsheet
```

3. Pass an URL as an argument from the command line. Please run the following:
```python
pipenv run python spiders/catch_fish_scraper.py --external-scrape-urls put_your_url_here
```
### Output Results
All the scraped information and the created report are saved under `mondu_website_scrapper/scraped_results`.

### Export Results
To export the report csv file to the pre-defined Gsheet, please run the following:
```python
pipenv run python gsheet_api/export2_gsheet.py
```
The script will create a new worksheet named by
`Web-Scraper-Report-{the timestamp when sheet is created}`. See the following image:
![Alt text](/images/google_sheet_export.png?raw=true "Mondu-Web-Scraper-Result")
