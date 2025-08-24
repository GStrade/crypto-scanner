from tradingview_ta import TA_Handler, Interval

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
