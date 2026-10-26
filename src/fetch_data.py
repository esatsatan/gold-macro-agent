import sqlite3
import os
import yfinance as yf
import pandas as pd
from .database import DB_PATH, init_db

def fetch_and_save_market_data():
    init_db()
    print("⏳ Yahoo Finance üzerinden geçmiş veriler toplu olarak indiriliyor...")

    # İki sembolü aynı anda indirip Close (Kapanış) fiyatlarını alıyoruz
    data = yf.download(["GC=F", "USDTRY=X"], period="2y", progress=False)
    
    if data.empty or 'Close' not in data:
        print("❌ Yahoo Finance verisi boş döndü!")
        return

    df = data['Close'].rename(columns={'GC=F': 'xau_usd', 'USDTRY=X': 'usd_try'})

    # Eksik verileri (tatil günleri vb.) önceki günün değeriyle dolduruyoruz (Forward Fill)
    df = df.ffill().dropna()

    if df.empty:
        print("❌ Veriler hizalandıktan sonra DataFrame boş kaldı!")
        return

    # Tarih formatını temizleme (YYYY-MM-DD)
    df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')

    # Teorik Gram Altın Hesaplama (TL/gram)
    df['gram_gold_try'] = (df['xau_usd'] / 31.1034768) * df['usd_try']
    df['gram_gold_try'] = df['gram_gold_try'].round(2)

    # SQLite Veritabanına Yazma
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    records_added = 0
    for date, row in df.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO market_data (date, xau_usd, usd_try, gram_gold_try)
            VALUES (?, ?, ?, ?)
        """, (date, float(row['xau_usd']), float(row['usd_try']), float(row['gram_gold_try'])))
        records_added += 1

    conn.commit()
    conn.close()
    print(f"✅ Toplam {records_added} günlük piyasa verisi SQLite veritabanına başarıyla aktarıldı.")

if __name__ == "__main__":
    fetch_and_save_market_data()