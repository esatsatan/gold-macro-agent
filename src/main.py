from fastapi import FastAPI
import sqlite3
import pandas as pd
import os
from .database import DB_PATH
from . import fetch_data
from . import predict

app = FastAPI(title="Gold Macro Forecast API")

@app.get("/forecast")
def get_forecast():
    fetch_data.fetch_and_save_market_data()
    predict.run_forecast()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT target_date, predicted_gram_gold, lower_bound_95, upper_bound_95 
        FROM forecasts 
        WHERE forecast_date = DATE('now')
    """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "date": row[0],
            "predicted_gram_gold": row[1],
            "lower_bound_95": row[2],
            "upper_bound_95": row[3]
        })

    return {"status": "success", "forecasts": result}