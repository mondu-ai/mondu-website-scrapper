import pandas as pd
from gspread.exceptions import WorksheetNotFound

from mondu_website_scrapper.gsheet_api.gsheet_settings import (
    CLIENT_SECRET_JSON,
    SCOPES,
    SPREADSHEET_NAME,
)
from mondu_website_scrapper.gsheet_api.utils import get_gsheet_client


def read_from_gsheet(
    input_columns: list,
    spreadsheet_name: str = None,
    worksheet_name: str = "Marketing-Input-Data",
):
    """
    read value from the given gsheet

    Returns: a dataframe
    """
    if spreadsheet_name is None:
        spreadsheet_name = SPREADSHEET_NAME
    gsheet_client = get_gsheet_client(
        client_secret_json=CLIENT_SECRET_JSON, scopes=SCOPES
    )

    spreadsheet = gsheet_client.open(spreadsheet_name)
    if worksheet_name in [sheet.title for sheet in spreadsheet.worksheets()]:
        input_worksheet = spreadsheet.worksheet(worksheet_name)
        return pd.DataFrame(input_worksheet.get_all_records(), columns=input_columns)

    raise WorksheetNotFound(f"{worksheet_name} not found under the given spreadsheet")
