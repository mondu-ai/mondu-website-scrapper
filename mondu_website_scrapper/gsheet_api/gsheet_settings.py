from pathlib import Path

import os

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]


CLIENT_SECRET_JSON = Path(__file__).parent / "client_secret.json"
EXPORT_DATA_FOLDER = Path(__file__).parent / "scraped_results"
SPREADSHEET_NAME = "Mondu-Web-Scraper-Data-Import-Export"
