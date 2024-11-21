import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from sklearn.preprocessing import StandardScaler
from airflow import DAG
from airflow.operators.python import PythonOperator
# Configuration
GOOGLE_SHEETS_CREDENTIALS = '/home/admin/airflow/creds/credentials.json'
GOOGLE_SHEET_NAME = 'data_model'
INPUT_WORKSHEET_NAME = 'Train Data'
OUTPUT_WORKSHEET_NAME = 'Processed Data'

def download_data():
    # Authentication 
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS, scopes=scope)
    client = gspread.authorize(credentials)

    sheet = client.open(GOOGLE_SHEET_NAME)

    try:
        worksheet = sheet.worksheet(INPUT_WORKSHEET_NAME)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        df.drop(columns=["Unnamed: 0"], inplace=True)
        df.to_csv('/tmp/data.csv', index=False)

    except gspread.exceptions.WorksheetNotFound:
        print("Worksheet not found")

def data_cleanup():
    # Dropping rows with missing values and duplicate rows
    df = pd.read_csv('/tmp/data.csv')
    df = df.dropna()
    df = df.drop_duplicates()
    df.to_csv('/tmp/data_cleaned.csv', index=False)

def data_processing():
    df = pd.read_csv('/tmp/data_cleaned.csv')

    # Scaling numerical columns except price
    numerical_columns = df.select_dtypes(include=['number']).columns
    columns_to_scale = [col for col in numerical_columns if col != 'price_in_pln']
    scaler = StandardScaler()
    df[columns_to_scale] = scaler.fit_transform(df[columns_to_scale])
    df.to_csv('/tmp/data_processed.csv')

def upload_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDENTIALS, scopes=scope)
    client = gspread.authorize(credentials)

    sheet = client.open(GOOGLE_SHEET_NAME)
    data = pd.read_csv('/tmp/data_processed.csv')
    try:
        worksheet = sheet.worksheet(OUTPUT_WORKSHEET_NAME)

    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=OUTPUT_WORKSHEET_NAME, rows=str(len(data)), cols=str(len(data.columns)))
    worksheet.clear()
    worksheet.update([data.columns.values.tolist()] + data.values.tolist())

with DAG(
    'download_and_process_data',
    schedule_interval=None,
    catchup=False,
) as dag:
    # Task: download data from google sheets
    download_task = PythonOperator(
        task_id='download_data',
        python_callable=download_data
    )
    # Task: clean data (missing and dupllicate values)
    cleanup_task = PythonOperator(
        task_id='data_cleanup',
        python_callable=data_cleanup
    )
    # Task: data processing - scaling numeric columns
    processing_task = PythonOperator(
        task_id = 'data_processing',
        python_callable=data_processing
    )
    # Task: upload processed data to google sheets
    upload_task = PythonOperator(
        task_id = 'data_upload',
        python_callable=upload_data
    )

    download_task >> cleanup_task >> processing_task >> upload_task