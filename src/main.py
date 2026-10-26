from fastapi import FastAPI
import subprocess
import sqlite3
import pandas as pd
import os
from database import DB_PATH

app = FastAPI(title="Gold Macro Forecast API")

@app.get("/forecast")
def get_forecast():
    # 1. Her istek geldiğinde veriyi ve modeli çalıştır
    import fetch_data
    import predict
    
    fetch_data.fetch_and_save_market_data()
    predict.run_forecast()

    # 2. SQLite'tan en son üretilen tahminleri okuyup n8n'e dön
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