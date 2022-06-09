import json
import logging
import os
from pathlib import Path
from typing import Union

import gspread
from dotenv import find_dotenv, load_dotenv
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials

from .gsheet_settings import ENV_FILE

load_dotenv(find_dotenv(ENV_FILE), verbose=True)

GSHEET_PRIVATE_KEY_ID = os.getenv("GSHEET_PRIVATE_KEY_ID")
GSHEET_PRIVATE_KEY = os.getenv("GSHEET_PRIVATE_KEY")


def get_gsheet_credential(client_secret_file: Union[Path, str]) -> dict:
    """
    create gsheet credential json file by reading credentials from .env

    Returns: client credential json file
    """
    # load_dotenv(os.path.join(Path(__file__).parent.parent, ".env"))

    with open(client_secret_file, "r", encoding="utf-8") as file:
        client_secret = json.load(file)
        client_secret["private_key_id"] = GSHEET_PRIVATE_KEY_ID
        client_secret["private_key"] = GSHEET_PRIVATE_KEY

    return client_secret


def get_gsheet_client(client_secret: Union[Path, dict], scopes: list[str]):
    """
    get the google sheet client

    Returns: return google sheet client
    """
    if isinstance(client_secret, Path):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            client_secret,
            scopes,
        )
    elif isinstance(client_secret, dict):
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            client_secret,
            scopes,
        )
    else:
        raise Exception("client secret should be either a dict or a path to a file")

    return gspread.authorize(credentials)


def get_report_file_name(export_data_folder: Union[Path, str]):
    """
    get the report csv file from the export data folder

    Raises: raise error if file not found
    Returns: file name
    """

    for file in os.listdir(export_data_folder):
        if file.endswith("__report.csv"):
            return export_data_folder / file


def create_worksheet(
    gsheet_client: object,
    spreadsheet_name: str,
    title: str,
    rows: int = 1000,
    cols: int = 50,
):
    """
    create a new worksheet in the current spreadsheet

    Returns: sheet id of the new created worksheet
    """
    spreadsheet = gsheet_client.open(spreadsheet_name)

    try:
        spreadsheet.add_worksheet(title=title, rows=rows, cols=cols)
    except APIError as error:

        logging.info("some error ocurred %s", error)
    return spreadsheet.worksheet(title).id


def update_worksheet(
    export_data_folder: Union[Path, str],
    gsheet_client: object,
    spreadsheet_name: str,
    worksheet_id: str,
) -> dict:
    """
    update contents into worksheet
    Returns: a dictionary of response dict
    """

    spreadsheet = gsheet_client.open(spreadsheet_name)

    report_file_path = get_report_file_name(export_data_folder)

    with open(report_file_path, "r", encoding="utf-8") as file:
        contents = file.read()

    body = {
        "requests": [
            {
                "pasteData": {
                    "coordinate": {"sheetId": worksheet_id},
                    "data": contents,
                    "type": "PASTE_NORMAL",
                    "delimiter": ",",
                }
            }
        ]
    }

    return spreadsheet.batch_update(body=body)
