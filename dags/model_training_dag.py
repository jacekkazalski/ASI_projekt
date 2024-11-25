import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from joblib import dump
from airflow import DAG
from airflow.operators.python import PythonOperator

LOCAL_CSV_PATH = "/opt/airflow/data/data_processed.csv"
REPORT_PATH = "/opt/airflow/reports/model_report.txt"
x_train, x_test, y_train, y_test = None, None, None, None
def load_data():
    # Load data from csv and split into train and test dataset
    global x_train, x_test, y_train, y_test
    df = pd.read_csv(LOCAL_CSV_PATH)
    x = df.drop(columns=['price_in_pln', 'Unnamed: 0'])
    y = df['price_in_pln']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=0)

def train_model():
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
    dump(model, "/opt/airflow/models/model.joblib")

with DAG(
    'model_training',
    schedule_interval=None,
    catchup=False,
) as dag:
    # Task load and split data
    load_task = PythonOperator(
        task_id='load_data'
        python_callable=load_data
    )
    # Task train model and generate a report
    train_task = PythonOperator(
        task_id='train_model'
        python_callable=train_model
    )

    load_task >> train_task