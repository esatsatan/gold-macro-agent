import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gold_macro.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Günlük Piyasa Fiyatları Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            date TEXT PRIMARY KEY,
            xau_usd REAL,
            usd_try REAL,
            gram_gold_try REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Üretilecek Model Tahminleri Tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forecasts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            forecast_date TEXT,
            target_date TEXT,
            model_name TEXT,
            predicted_gram_gold REAL,
            lower_bound_80 REAL,
            upper_bound_80 REAL,
            lower_bound_95 REAL,
            upper_bound_95 REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("✅ SQLite veritabanı ve tablolar başarıyla hazırlandı.")

if __name__ == "__main__":
    init_db()