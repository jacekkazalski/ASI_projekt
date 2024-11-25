import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from joblib import dump

LOCAL_CSV_PATH = r'C:\Users\Admin\Desktop\studia\asi\s22393_CarPricePrediction\data\data_processed.csv'
REPORT_PATH = '/../reports/model_report.txtS'
x_train, x_test, y_train, y_test = None, None, None, None
def load_data():
    global x_train, x_test, y_train, y_test
    df = pd.read_csv(LOCAL_CSV_PATH)
    x = df.drop(columns=['price_in_pln', 'Unnamed: 0'])
    y = df['price_in_pln']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=0)

def train_model():
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

    r2 = r2_score(y_test, preds)
    mae = mean_absolute_error(y_test, preds)

    with open(REPORT_PATH, "w") as report_file:
        report_file.write("Model Performance Report\n")
        report_file.write("========================\n")
        report_file.write(f"R^2: {r2:.4f}\n")
        report_file.write(f"Mean Absolute Error: {mae:.4f}\n")


load_data()
train_model()