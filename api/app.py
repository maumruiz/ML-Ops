import joblib
from fastapi import FastAPI
import pandas as pd

app = FastAPI()

@app.get("/")
def read_root():
    return { "Spike api": "A fastapi implementation for milk price prediction." }

@app.get("/api/predict")
def predict(year: int = 2020, month: int = 1):
    model = joblib.load("/models/model.pkl")
    feature_data = pd.read_csv('/models/feature_data.csv')

    query = feature_data[(feature_data['ano'] == year) & (feature_data['mes'] == month)]
    if query.empty:
        return {"error": 'Fecha no encontrada'}
    else:
        features = query.to_numpy()[:,2:]
        prediction = model.predict(features)
        return { "result": prediction.flatten()[0] }