from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
import gspread
from google.oauth2.service_account import Credentials

# Configuration
LOCAL_CSV_PATH = '/home/admin/airflow/data/data_cleaned.csv'
GOOGLE_SHEETS_CREDENTIALS = '/home/admin/airflow/creds/credentials.json'
GOOGLE_SHEET_NAME = 'data_model'

# Reads the csv and splits it into two sets
def split_csv():
    df = pd.read_csv(LOCAL_CSV_PATH)    
    train, test = train_test_split(df, test_size=0.3, random_state=42)
    train.to_csv('/tmp/train.csv', index=False)
    test.to_csv('/tmp/test.csv', index=False)

def upload_to_gsheets():
    # Authenticate with Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS, scopes=scope)
    client = gspread.authorize(credentials)

    # Open the target Google Sheet
    sheet = client.open(GOOGLE_SHEET_NAME)

    # Upload Train Data
    train_data = pd.read_csv('/tmp/train.csv')
    try:
        train_sheet = sheet.worksheet("Train Data")
        sheet.del_worksheet(train_sheet) 
    except gspread.exceptions.WorksheetNotFound:
        pass
    train_sheet = sheet.add_worksheet(title="Train Data", rows=str(len(train_data)), cols=str(len(train_data.columns)))
    train_sheet.update([train_data.columns.values.tolist()] + train_data.values.tolist())

    # Upload Test Data
    test_data = pd.read_csv('/tmp/test.csv')
    try:
        test_sheet = sheet.worksheet("Test Data")
        sheet.del_worksheet(test_sheet)
    except gspread.exceptions.WorksheetNotFound:
        pass
    test_sheet = sheet.add_worksheet(title="Test Data", rows=str(len(test_data)), cols=str(len(test_data.columns)))
    test_sheet.update([test_data.columns.values.tolist()] + test_data.values.tolist())


with DAG(
    'split_and_upload_gsheet',
    schedule_interval=None,
    catchup=False,
) as dag:
    # Task: load and split data
    split_task = PythonOperator(
        task_id='split_csv',
        python_callable=split_csv,
    )
    #Task: upload data
    upload_task = PythonOperator(
        task_id='upload_to_gsheets',
        python_callable=upload_to_gsheets,
    )

    split_task >> upload_task
