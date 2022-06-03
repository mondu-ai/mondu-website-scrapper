""" Define Mondu scrapper item pipelines here"""

# pylint: disable=attribute-defined-outside-init
import logging
from scrapy.exporters import CsvItemExporter
from mondu_website_scrapper import items
from mondu_website_scrapper.utils import extract_categories_from_wappalyzer


def item_type(item):
    """
    get and lower item class name
    """
    return type(item).__name__.lower()


class MonduWebsiteScrapperPipeline:
    """
    this is the pipeline taking sccrapped items, processing items,
    and then exporting it into csv file.
    """

    defined_items = [
        name.lower() for name, _ in items.__dict__.items() if "Item" in name
    ]

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

    def open_spider(self, spider):  # pylint: disable=unused-argument
        """
        open file, define exporter and start exporting
        """
        self.files = dict(
            [
                (name, open(self.file_folder / f"{name}.csv", "w+b"))
                for name in self.defined_items
            ]
        )
        self.exporters = dict(
            [(name, CsvItemExporter(self.files[name])) for name in self.defined_items]
        )
        logging.info("Starting exporting into csv...")

        for exporter in self.exporters.values():
            exporter.start_exporting()

    def close_spider(self, spider):  # pylint: disable=unused-argument
        """
        finishining exporting and close the file
        """
        logging.info("Finishing exporting into csv...")
        for exporter in self.exporters.values():
            exporter.finish_exporting()
        for file in self.files.values():
            file.close()

    def process_item(self, item, spider):  # pylint: disable=unused-argument
        """
        process items scrapped from web.
        1. only the wappalyzer item needs to be processed. check function
        extract_categories_from_wappalyzer for more details
        """
        item_name = item_type(item)
        if item_name in set(self.defined_items):
            if item_name == "generalinformationitem":
                item["wappalyzer"] = extract_categories_from_wappalyzer(
                    item["wappalyzer"]
                )
            logging.info("Exporting items into csv...")
            self.exporters[item_name].export_item(item)
        return item
