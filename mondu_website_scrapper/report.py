""" create final scraped report"""
import ast
import csv
import logging
from dataclasses import dataclass
from functools import reduce

import numpy as np
import pandas as pd
from scrapy.utils.project import get_project_settings

from mondu_website_scrapper import items
from mondu_website_scrapper.utils import is_empty_file, normalize_phone_format

settings = get_project_settings()


@dataclass
class CreateReportDataSet:
    """
    a class to create a final scraping report

    """

    join_index: str = "company_url"
    wappalyzer_data_column: str = "wappalyzer"
    phone_data_column: str = "phone"
    leadspider_name: str = "findingnemo"
    wappalyzed_data_keys: list[str] = None

    def _eng_general_info_item(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        engineer scraped general information item
        1. wappalyze data is flatterned
        2. create a new column tagged_as_b2b

        Returns: engineered dataframe
        """

        wappalyzed_df = self._normalize_wappalyzer_data(
            data[self.wappalyzer_data_column]
        )
        self.wappalyzed_data_keys = wappalyzed_df.columns.tolist()
        data.drop(self.wappalyzer_data_column, inplace=True, axis=1)
        data.loc[:, "tagged_as_b2b"] = np.where(
            data["tagged_by_b2b_words"].isna(), False, True
        )

        data_concat = pd.concat([data, wappalyzed_df], axis=1).set_index(
            self.join_index
        )
        for col in ["webshop_system", "Ecommerce"]:
            data_concat[col] = data_concat[col].apply(
                lambda x: x.lower() if not pd.isna(x) else x
            )

        data_concat = data_concat.assign(
            webshop_system=data_concat["webshop_system"].mask(
                data_concat["webshop_system"].isnull(), data_concat["Ecommerce"]
            )
        )

        data_concat["web_system/ecommerce"] = (
            data_concat["webshop_system"] + "," + data_concat["Ecommerce"]
        )

        data_concat["web_system/ecommerce"] = data_concat["web_system/ecommerce"].apply(
            lambda x: ",".join(list(set(x.split(",")))) if not pd.isna(x) else x
        )
        return data_concat

    def _eng_price_item(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        engineer scrapted price item
        for each company url, calculate the average of price and total number of products

        Returns: engineered dataframe
        """
        return (
            data.groupby(self.join_index)
            .agg(
                {
                    "products_avg_price": "mean",
                    "currency": "first",
                    "products_quantity": "sum",
                }
            )
            .rename(columns={"products_quantity": "total_num_products"})
        )

    def _eng_contact_information_item(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        engineer scraped contact item

        for the same company url, concat all the results together and drop duplicates

        Returns: engineered dataframe
        """
        data.loc[:, self.phone_data_column] = data[self.phone_data_column].apply(
            lambda x: normalize_phone_format(x, country_code=["43", "49"])
        )

        for col in [i for i in data.columns if i != self.join_index]:
            data.replace(np.nan, "nan", inplace=True)
            data[col] = data.groupby(self.join_index)[col].transform(
                lambda x: ",".join(x)
            )

        data_drop = data.drop_duplicates()

        for col in data_drop.columns:
            data_drop.loc[:, col] = data_drop[col].apply(
                lambda x: ";".join([x for x in x.split(",") if x != "nan"])
            )
        return data_drop.set_index(self.join_index)

    def _normalize_wappalyzer_data(self, wappalyzer_data: pd.Series) -> pd.DataFrame:

        """
        normalize the result of wappalyzed api data and create a pandas dataframe
        1. convert to json
        2.apply json normalize to the whole column

        Returns: a pandas dataframe
        """
        wappalyzer_data = wappalyzer_data.str.replace("'", '"', regex=True)

        return pd.json_normalize(wappalyzer_data.apply(ast.literal_eval).tolist())

    def _load_item_data(self):
        """
        left join all engineered data frames together,
        and save the generated report file under scraped results
        """

        file_names = [
            name.lower() for name, _ in items.__dict__.items() if "Item" in name
        ]
        file_paths = {
            file_name: settings["FILE_FOLDER"] / f"{file_name}.csv"
            for file_name in file_names
        }

        dfs = {
            file_name: pd.read_csv(file_path)
            for file_name, file_path in file_paths.items()
            if not is_empty_file(file_path)
        }

        eng_item_data_dict = {}
        for file_name, data in dfs.items():
            if "general" in file_name:
                eng_item_data_dict[file_name] = self._eng_general_info_item(data)
            elif "price" in file_name:
                eng_item_data_dict[file_name] = self._eng_price_item(data)
            else:
                eng_item_data_dict[file_name] = self._eng_contact_information_item(data)

        return eng_item_data_dict

    def join_all_scraped_items(self):
        """
        left join all engineered data frames together,
        and save the generated report file under scraped results
        """
        eng_item_data_dict = self._load_item_data()

        report_df = reduce(
            lambda df1, df2: df1.join(df2, on=self.join_index),
            eng_item_data_dict.values(),
        )

        report_df.dropna(how="all", axis=1, inplace=True)

        save_file_path = settings["FILE_FOLDER"] / f"{self.leadspider_name}__report.csv"

        report_df.to_csv(save_file_path, sep=",", quoting=csv.QUOTE_NONNUMERIC)
        logging.info(
            "final report dataframe is of %s, saved under %s",
            report_df.shape,
            save_file_path,
        )
