# core/sheet_reader.py
import gspread
import os
import json

#from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials

from datetime import datetime

from config.config import (
    CREDENTIAL_FILE,
    RECRUIT_SHEET_URL,
    RECRUIT_TAB_NAME,
    COL_POSITION,
    COL_CONTENT,
    COL_THREAD,
    COL_TOPIC,
    COL_IMAGE,
    COL_POSTED,
    COL_PROFILE,
    COL_DATE,
    MAX_POSTS_PER_RUN,
)

# =========================
# CONNECT GOOGLE SHEET
# =========================
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
    return client.open_by_url(RECRUIT_SHEET_URL).worksheet(RECRUIT_TAB_NAME)


# =========================
# READ ALL ROWS
# =========================
def get_all_rows():
    sheet = connect_sheet()
    return sheet.get_all_records()


# =========================
# GET UNPOSTED ROWS
# =========================
def get_unposted_rows(limit=MAX_POSTS_PER_RUN):
    """
    Trả về list:
    [
        {
            "row_index": 2,
            "data": { ...row data... }
        }
    ]
    """
    sheet = connect_sheet()
    rows = sheet.get_all_records()

    results = []
    for idx, row in enumerate(rows, start=2):  # start=2 vì row 1 là header
        posted = str(row.get(COL_POSTED, "")).strip().upper()

        if posted == "YES":
            continue

        results.append({
            "row_index": idx,
            "data": row
        })

        if len(results) >= limit:
            break

    return results


# =========================
# MARK AS POSTED
# =========================
def mark_posted(row_index: int, threads_profile: str):
    sheet = connect_sheet()
    today = datetime.now().strftime("%Y-%m-%d")

    sheet.update_cell(row_index, _col_index(COL_POSTED), "YES")
    sheet.update_cell(row_index, _col_index(COL_PROFILE), threads_profile)
    sheet.update_cell(row_index, _col_index(COL_DATE), today)


# =========================
# INTERNAL: FIND COLUMN INDEX
# =========================
def _col_index(col_name: str) -> int:
    """
    Tìm index cột theo tên (1-based)
    """
    sheet = connect_sheet()
    headers = sheet.row_values(1)

    for i, h in enumerate(headers, start=1):
        if h.strip() == col_name:
            return i

    raise Exception(f"❌ Không tìm thấy cột: {col_name}")
