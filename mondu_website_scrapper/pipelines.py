""" Define Mondu scrapper item pipelines here"""

# pylint: disable=attribute-defined-outside-init
import logging
from scrapy.exporters import CsvItemExporter
from mondu_website_scrapper.utils import extract_categories_from_wappalyzer


class MonduWebsiteScrapperPipeline:
    """
    this is the pipeline taking sccrapped items, processing items,
    and then exporting it into csv file.
    """

    def __init__(self, file_folder):
        self.file_folder = file_folder
        self.file_folder.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_crawler(cls, crawler):
        """
        get settings from settings.py
        Returns: class with settings
        """
        return cls(
            file_folder=crawler.settings.get("FILE_FOLDE"),
        )

    def open_spider(self, spider):
        """
        open file, define exporter and start exporting
        """
        logging.info("Starting exporting into csv...")
        # with open(self.file_folder / f"{spider.name}.csv", "wb") as self.file:
        self.file = open(self.file_folder / f"{spider.name}.csv", "wb")
        self.exporter = CsvItemExporter(self.file)
        self.exporter.start_exporting()

    def process_item(self, item, spider):  # pylint: disable=unused-argument

        """
        process items scrapped from web.
        1. only the wappalyzer item needs to be processed. check function
        extract_categories_from_wappalyzer for more details
        """
        item["wappalyzer"] = extract_categories_from_wappalyzer(item["wappalyzer"])
        logging.info("Exporting items into csv...")
        self.exporter.export_item(item)

        return item

    def close_spider(self, spider):  # pylint: disable=unused-argument

        """
        finishining exporting and close the file
        """
        logging.info("Finishing exporting into csv...")
        self.exporter.finish_exporting()
        self.file.close()
