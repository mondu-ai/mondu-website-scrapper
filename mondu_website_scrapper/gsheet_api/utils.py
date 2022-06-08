import fnmatch
import json
import logging
import os
from pathlib import Path
from typing import Union

import gspread
from gspread.exceptions import APIError
from oauth2client.service_account import ServiceAccountCredentials


def get_gsheet_client(client_secret_json: json, scopes: list[str]):
    """
    get the google sheet client

    Returns: return google sheet client
    """

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        client_secret_json,
        scopes,
    )
    return gspread.authorize(credentials)


def get_report_file_name(export_data_folder: Union[Path, str]):
    """
    get the report csv file from the export data folder

    Raises: raise error if file not found
    Returns: file name
    """

    for file in os.listdir(export_data_folder):
        if fnmatch.fnmatch(file, "__report.cvs"):
            return file
        raise ValueError("report csv file not found")


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

    report_file_name = get_report_file_name(export_data_folder)

    with open(report_file_name, "r", encoding="utf-8") as file:
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
