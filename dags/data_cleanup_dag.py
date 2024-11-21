import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# Configuration
GOOGLE_SHEETS_CREDENTIALS = '/home/admin/airflow/creds/credentials.json'
GOOGLE_SHEET_NAME = 'data_model'
WORKSHEET_NAME = 'Train Data'

def download_data():
    # Authentication 
    print("downloading")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS, scopes=scope)
    client = gspread.authorize(credentials)

    sheet = client.open(GOOGLE_SHEET_NAME)

    try:
        train_sheet = sheet.worksheet(WORKSHEET_NAME)
        data = train_sheet.get_all_records()
        df = pd.DataFrame(data)
        df.drop(columns=["Unnamed: 0"], inplace=True)
        df.to_csv('/tmp/data.csv', index=False)

    except gspread.exceptions.WorksheetNotFound:
        print("Worksheet not found")

def data_cleanup():
    df = pd.read_csv('/tmp/data.csv')
    df = df.dropna()
    df = df.drop_duplicates()
    df.to_csv('/tmp/data_cleaned.csv', index=False)

def data_processing():
    df = pd.read_csv('/tmp/data_cleaned.csv')
download_data()