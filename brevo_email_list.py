import requests
import os

from email_sheet_reader import get_all_rows
from dotenv import load_dotenv
load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_LIST_ID = 2  # change this

def add_contact_to_brevo(email, fname = None, lname = None):
    url = "https://api.brevo.com/v3/contacts"

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "api-key": BREVO_API_KEY,
    }

    attributes = {}
    if fname:
        attributes["FIRSTNAME"] = fname
    if lname:
        attributes["LASTNAME"] = lname
    
    payload = {
        "email": email,
        "attributes": attributes,
        "listIds": [BREVO_LIST_ID],
        "updateEnabled": True
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code not in (200, 201):
        print(f"❌ Failed for {email}: {response.text}")
    else:
        print(f"✅ Added/Updated: {email}")

def delete_contact(email):
    url = f"https://api.brevo.com/v3/contacts/{email}"
    headers = {"api-key": BREVO_API_KEY}

    r = requests.delete(url, headers=headers)

    if r.status_code == 204:
        print(f"🗑 Deleted {email}")
    else:
        print(f"❌ {email}: {r.status_code} {r.text}")

def delete_from_sheet():
    rows = get_all_rows()
    for row in rows:
        email = row.get("Email")
        if email:
            delete_contact(email)

def sync_contacts():
    rows = get_all_rows()
    for row in rows:
        email = row.get("Email")
        if not email:
            continue
        
        email = email.strip().lower()
        add_contact_to_brevo(
            email,
            row.get("FirstName"),
            row.get("LastName"),
        )

def menu():
    print("\nBrevo Contact Manager")
    print("1. Add / Update contacts from Google Sheet")
    print("2. Delete contacts from Google Sheet")
    print("3. Exit")

    return input("Choose an option: ").strip()

while True:
    choice = menu()

    if choice == "1":
        sync_contacts()
    elif choice == "2":
        delete_from_sheet()
    elif choice == "3":
        break
    else:
        print("Invalid choice")

