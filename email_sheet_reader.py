import gspread
import os
import json

from google.oauth2.service_account import Credentials
from datetime import datetime

from config.config import (
    CREDENTIAL_FILE,
    EMAIL_SHEET_URL,
    EMAIL_TAB_NAME,
    COL_EMAIL,
)

def connect_sheet():
    scope = [      
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    
    # Try to load credentials from environment variable first
    creds_json = os.getenv('GOOGLE_CREDENTIALS')
    
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            creds = Credentials.from_service_account_info(
                creds_dict, scopes=scope
            )
        except Exception as e:
            raise ValueError(f"Failed to parse GOOGLE_CREDENTIALS environment variable: {e}")
    else:
        # Fallback to credentials.json file if env variable not set
        if not os.path.exists(CREDENTIAL_FILE):
            raise FileNotFoundError(
                f"credentials.json not found and GOOGLE_CREDENTIALS environment variable not set. "
                f"Please set GOOGLE_CREDENTIALS or provide credentials.json"
            )
        creds = Credentials.from_service_account_file(
            CREDENTIAL_FILE, scopes=scope
        )
    
    client = gspread.authorize(creds)
    return client.open_by_url(EMAIL_SHEET_URL).worksheet(EMAIL_TAB_NAME)

def get_all_rows():
    sheet = connect_sheet()
    return sheet.get_all_records()

