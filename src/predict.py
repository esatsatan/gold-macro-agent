import sqlite3
import os
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from arch import arch_model
from database import DB_PATH

def run_forecast():
    print("⏳ SQLite veritabanından geçmiş piyasa verileri yükleniyor...")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT date, gram_gold_try FROM market_data ORDER BY date ASC", conn, parse_dates=['date'])
    conn.close()

    if df.empty or len(df) < 50:
        print("❌ Model için yeterli geçmiş veri bulunamadı!")
        return

    # Pandas uyarılarını önlemek için index ataması
    df = df.set_index('date')
    
    # Eksik günleri tamamlayıp iş günü (Business Day) frekansı tanımlıyoruz
    df = df.asfreq('B').ffill()
    
    prices = df['gram_gold_try']

    # 1. ARIMA Modeli ile Fiyat Trend Tahmini (7 Günlük)
    print("📈 ARIMA(1,1,1) modeli eğitiliyor (Fiyat Trend Projeksiyonu)...")
    model_arima = ARIMA(prices, order=(1, 1, 1))
    results_arima = model_arima.fit()
    
    forecast_obj = results_arima.get_forecast(steps=7)
    predicted_means = forecast_obj.predicted_mean
    
    # Gelecek 7 iş günü için tarih aralığı
    future_dates = predicted_means.index

    # 2. GARCH(1,1) Modeli ile Volatilite (Risk Bandı) Hesaplama
    print("⚡ GARCH(1,1) modeli eğitiliyor (Piyasa Volatilitesi & Risk Analizi)...")
    returns = prices.pct_change().dropna() * 100  # Yüzdelik getiri serisi
    
    garch = arch_model(returns, vol='Garch', p=1, q=1, mean='Constant', dist='Normal')
    res_garch = garch.fit(disp='off')
    
    # Son günün koşullu volatilitesini alıyoruz
    conditional_volatility = res_garch.conditional_volatility.iloc[-1]
    
    # SQLite veritabanına kayıt bağlantısı
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n📊 7 GÜNLÜK GRAM ALTIN EKONOMETRİK TAHMİN RAPORU:")
    print("-" * 65)

    for i, date in enumerate(future_dates):
        pred_price = predicted_means.iloc[i]
        
        # Gün ilerledikçe belirsizlik karekök kuralıyla (sqrt(h)) artar
        h = i + 1
        std_h = (conditional_volatility / 100) * pred_price * np.sqrt(h)
        
        # %80 (z=1.28) ve %95 (z=1.96) güven aralıkları
        lower_80 = pred_price - 1.28 * std_h
        upper_80 = pred_price + 1.28 * std_h
        
        lower_95 = pred_price - 1.96 * std_h
        upper_95 = pred_price + 1.96 * std_h

        date_str = date.strftime('%Y-%m-%d')
        print(f"📅 Tarih: {date_str} | 🎯 Tahmin: {pred_price:.2f} TL | %95 Bant: [{lower_95:.2f} - {upper_95:.2f}]")

        # SQLite forecasts tablosuna yazma
        cursor.execute("""
            INSERT INTO forecasts (forecast_date, target_date, model_name, predicted_gram_gold, lower_bound_80, upper_bound_80, lower_bound_95, upper_bound_95)
            VALUES (DATE('now'), ?, 'ARIMA-GARCH', ?, ?, ?, ?, ?)
        """, (date_str, float(pred_price), float(lower_80), float(upper_80), float(lower_95), float(upper_95)))
        
    conn.commit()
    conn.close()
    print("-" * 65)
    print("✅ 7 günlük tahmin ve risk bantları başarıyla SQLite veritabanına kaydedildi!")

if __name__ == "__main__":
    run_forecast()