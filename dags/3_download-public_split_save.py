from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
import gspread
from google.oauth2.service_account import Credentials
import kagglehub
import shutil
import os

# Configuration
GOOGLE_SHEETS_CREDENTIALS = '/opt/airflow/creds/credentials.json'
GOOGLE_SHEET_NAME = 'data_model'

# Downloads dataset from kaggle
def download_data():
    path = kagglehub.dataset_download("wspirat/poland-used-cars-offers")
    print("Dataset downloaded: %s", path)

    csv_path = os.path.join(path, "data.csv")

    df = pd.read_csv(csv_path)
    df.to_csv('/tmp/data.csv')

    
# Reads the csv and splits it into two sets
def split_csv():
    df = pd.read_csv('/tmp/data.csv')    
    model, fine_tuning = train_test_split(df, test_size=0.3, random_state=42)
    model.to_csv('/tmp/model.csv', index=False)
    fine_tuning.to_csv('/tmp/fine_tuning.csv', index=False)

def upload_to_gsheets():
    # Authenticate with Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS, scopes=scope)
    client = gspread.authorize(credentials)

    # Open the target Google Sheet
    sheet = client.open(GOOGLE_SHEET_NAME)

    # Upload Train Data
    model = pd.read_csv('/tmp/model.csv')
    try:
        model_sheet = sheet.worksheet("Model Data")
        sheet.del_worksheet(model_sheet) 
    except gspread.exceptions.WorksheetNotFound:
        pass    
    model_sheet = sheet.add_worksheet(title="Model Data", rows=str(len(model)), cols=str(len(model.columns)))
    model_sheet.update([model.columns.values.tolist()] + model.values.tolist())

    # Upload Test Data
    fine_tuning = pd.read_csv('/tmp/fine_tuning.csv')
    try:
        fine_tuning_sheet = sheet.worksheet("Fine-tuning Data")
        sheet.del_worksheet(fine_tuning_sheet)
    except gspread.exceptions.WorksheetNotFound:
        pass    
    fine_tuning_sheet = sheet.add_worksheet(title="Fine-tuning Data", rows=str(len(fine_tuning)), cols=str(len(fine_tuning.columns)))
    fine_tuning_sheet.update([fine_tuning.columns.values.tolist()] + fine_tuning.values.tolist())


with DAG(
    'download-public_split_save',
    schedule_interval=None,
    catchup=False,
) as dag:
    download_task = PythonOperator(
        task_id='download_data',
        python_callable=download_data,
    )
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

    download_task >> split_task >> upload_task
