import os
import sys

from gsheets import Sheets

# This is so that below import works
sys.path.append(os.path.realpath("."))

from src.config import *


def fetch_sheet_data(token_file, spreadsheet_id):
    """
     We fetch the google sheets given spreadsheet id and sheet id and then dump it into csv
     https://docs.google.com/spreadsheets/d/spreadsheetId/edit#gid=sheet_id

     Enable google drive API and Google Sheets API in google developer console. Check these APIs in OAuth consent screen
    """
    sheets_object = Sheets.from_files(token_file, "storages.json")
    sheets = sheets_object[spreadsheet_id]
    return sheets


def fetch(channel_config, app):
    sheets = fetch_sheet_data(channel_config[CLIENT_SECRET_FILE],
                              channel_config[SPREADSHEET_ID])

    sheets[channel_config[SHEET_ID]].to_csv(fetch_file_save_path,
                                            encoding="utf-8",
                                            dialect="excel")
