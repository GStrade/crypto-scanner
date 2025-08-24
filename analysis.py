from tradingview_ta import TA_Handler, Interval
import requests
import os

LUNAR_API = os.getenv("LUNARCRUSH_API")

# חישוב 4 טייק פרופיט לפי פיבונאצ'י
def calculate_fibonacci_tps(prices, entry_price):
    high, low = max(prices), min(prices)
    diff = high - low
    
    levels = {
        "TP1": round(low + diff * 0.236, 4),
        "TP2": round(low + diff * 0.382, 4),
        "TP3": round(low + diff * 0.5, 4),
        "TP4": round(low + diff * 0.618, 4),
    }
    return {k: v for k, v in levels.items() if v > entry_price}

# ניתוח טכני מ-TradingView
def get_tv_analysis(symbol: str):
    handler = TA_Handler(
        symbol=symbol.upper(),
        screener="crypto",
        exchange="BINANCE",
        interval=Interval.INTERVAL_1_DAY
    )
    analysis = handler.get_analysis()
    return analysis.summary

# רשימת מטבעות טרנדיים מ-LunarCrush
def get_trending_coins(limit=50):
    url = f"https://lunarcrush.com/api3/coins?sort=galaxy_score&limit={limit}"
    headers = {"Authorization": f"Bearer {LUNAR_API}"} if LUNAR_API else {}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            return [c["s"].upper() for c in data.get("data", [])]
        else:
            print("שגיאה ב-LunarCrush:", res.text)
            return []
    except Exception as e:
        print("שגיאה בחיבור ל-LunarCrush:", e)
        return []
