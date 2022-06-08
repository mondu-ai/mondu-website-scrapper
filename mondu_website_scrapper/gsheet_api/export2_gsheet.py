from datetime import datetime  # pylint: disable=missing-module-docstring
from pathlib import Path
from typing import Union

from .gsheet_settings import (
    CLIENT_SECRET_JSON,
    EXPORT_DATA_FOLDER,
    SCOPES,
    SPREADSHEET_NAME,
)
from .utils import create_worksheet, get_gsheet_client, update_worksheet


def export_report(
    export_data_folder: Union[Path, str],
    spreadsheet_name: str = None,
    worksheet_name: str = "Web-Scraper-Report",
):
    """
    export csv file into a pre-defined google sheet
    1. create gsheet api client
    2. create a new worksheet named as Web-Scraper-Report-{timestamp in
    format of year/month/day hour:min}
    3. export the csv file * __report.csv under scraped_results into new created worksheet

    """
    if spreadsheet_name is None:
        spreadsheet_name = SPREADSHEET_NAME
    gsheet_client = get_gsheet_client(
        client_secret_json=CLIENT_SECRET_JSON, scopes=SCOPES
    )
    now = datetime.now()
    dt_now = now.strftime("%Y/%m/%d %H:%M")

    current_worksheet_name = f"{worksheet_name}-{dt_now}"

    worksheet_id = create_worksheet(
        gsheet_client, spreadsheet_name=spreadsheet_name, title=current_worksheet_name
    )
    update_worksheet(
        export_data_folder,
        gsheet_client,
        spreadsheet_name=spreadsheet_name,
        worksheet_id=worksheet_id,
    )


if __name__ == "__main__":
    export_report(export_data_folder=EXPORT_DATA_FOLDER)
