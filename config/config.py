# config/config.py

# Google service account credentials
CREDENTIAL_FILE = "credentials.json"

# Google Sheet tuyển dụng
RECRUIT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1bBkKae805H60iWStPRNFP9noj_EWCGDwT40Z3pJmOt8/edit"
RECRUIT_TAB_NAME = "Recruitment"

# ===== TÊN CỘT (CHỐT) =====
COL_POSITION = "Position"        # A
COL_CONTENT = "Job Content"      # B
COL_THREAD = "Thread Content"    # C
COL_TOPIC = "Topic"              # D
COL_IMAGE = "Image URL"          # E
COL_POSTED = "Posted"            # F  (YES = skip)
COL_PROFILE = "ThreadsProfile"   # G
COL_DATE = "Date"                # H

# Hashtags mặc định
DEFAULT_HASHTAGS = [
    "#hiring",
    "#internship",
    "#recruitment",
    "#careers"
]

# Limit mỗi lần cron chạy
MAX_POSTS_PER_RUN = 1
