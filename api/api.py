from flask import Flask, request, jsonify
import joblib
import pandas as pd

model = joblib.load("./models/model.pkl")
encoder = joblib.load("./models/encoder.pkl")
scaler = joblib.load("./models/scaler.pkl")

NUMERIC_COLUMNS = ['mileage', 'engine_capacity', 'year']
CATEGORICAL_COLUMNS = ['brand', 'gearbox', 'fuel_type']

app = Flask(__name__)
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file found'}), 400

    file = request.files['file']

    try:
        data = pd.read_json(file)
        print("Uploaded DataFrame Columns:", data.columns.tolist())
    except Exception as e:
        return jsonify({'error': f'Cannot read the file: {e}'}), 400

    data[NUMERIC_COLUMNS] = scaler.transform(data[NUMERIC_COLUMNS])
    encoded_data = encoder.transform(data[CATEGORICAL_COLUMNS])
    encoded_columns = encoder.get_feature_names_out(CATEGORICAL_COLUMNS)
    encoded_df = pd.DataFrame(encoded_data, columns=encoded_columns, index=data.index)

    data = data.drop(columns=CATEGORICAL_COLUMNS)
    data = pd.concat([data, encoded_df], axis=1)

    predictions = model.predict(data)
    return jsonify({'predictions': predictions.tolist()})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)