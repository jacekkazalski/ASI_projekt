import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from joblib import dump
from airflow import DAG
from airflow.operators.python import PythonOperator
from google.oauth2.service_account import Credentials
import gspread
import numpy as np

GOOGLE_SHEETS_CREDENTIALS = '/opt/airflow/creds/credentials.json'
GOOGLE_SHEET_NAME = 'data_model'
INPUT_WORKSHEET_NAME = 'Processed Data'
REPORT_PATH = "/opt/airflow/reports/model_report.txt"

# Download processed data from google sheets
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

def split_data():
    # Split into train and test dataset
    df = pd.read_csv('/tmp/data.csv')
    x = df.drop(columns=['price_in_pln'])
    y = df['price_in_pln']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=0)

    x_train.to_csv('/tmp/x_train.csv', index=False)
    x_test.to_csv('/tmp/x_test.csv', index=False)
    y_train.to_csv('/tmp/y_train.csv', index=False)
    y_test.to_csv('/tmp/y_test.csv', index=False)

def train_model():
    x_train = pd.read_csv('/tmp/x_train.csv')
    x_test = pd.read_csv('/tmp/x_test.csv')
    y_train = pd.read_csv('/tmp/y_train.csv').squeeze()
    y_test = pd.read_csv('/tmp/y_test.csv').squeeze() 

    # Model training
    model = HistGradientBoostingRegressor(
        l2_regularization=2.208787572338781e-05,
        learning_rate=0.036087332404571744, 
        max_iter=512,
        max_leaf_nodes=64, 
        min_samples_leaf=3, 
        n_iter_no_change=18,
        random_state=0, 
        validation_fraction=None, 
        warm_start=True)
    
    model.fit(x_train, y_train)
    preds = model.predict(x_test)

    # Model results
    r2 = r2_score(y_test, preds)
    mae = mean_absolute_error(y_test, preds)

    # Saving results to txt file
    with open(REPORT_PATH, "a") as report_file:
        report_file.write("Model Performance Report\n")
        report_file.write("========================\n")
        report_file.write(f"R^2: {r2:.4f}\n")
        report_file.write(f"Mean Absolute Error: {mae:.4f}\n")

    # Save model to file
    dump(model, "/opt/airflow/models/model.pkl")

with DAG(
    'building_model',
    schedule_interval=None,
    catchup=False,
) as dag:
    # Task download data
    download_task = PythonOperator(
        task_id='download_data',
        python_callable=download_data
    )
    # Split data
    split_task = PythonOperator(
        task_id='split_data',
        python_callable=split_data
    )
    # Task train model and generate a report
    train_task = PythonOperator(
        task_id='train_model',
        python_callable=train_model
    )

    download_task >> split_task >> train_task