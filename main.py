from telegram import Bot
from config import TOKEN, CHAT_ID
from analysis import get_tv_analysis, calculate_fibonacci_tps
from charting import generate_chart
import yfinance as yf

bot = Bot(token=TOKEN)

def analyze_coin(symbol):
    # שליפת מחיר מהיסטוריית YF
    data = yf.Ticker(symbol + "-USD").history(period="1mo")
    entry = round(data["Close"].iloc[-1], 4)

    # חיווי טכני
    tv_summary = get_tv_analysis(symbol)

    # חישוב TP לפי פיבונאצ'י
    tps = calculate_fibonacci_tps(data["Close"].tolist(), entry)

    # סטופלוס = 0.786 פיבונאצ'י או 10% מתחת לכניסה
    stop = round(entry * 0.9, 4)

    # גרף
    chart = generate_chart(symbol, entry, stop, tps)

    # בניית טקסט
    text = f"""
📊 {symbol.upper()} (BINANCE)
💵 מחיר כניסה: {entry}
🎯 TP1: {tps.get('TP1','-')}
🎯 TP2: {tps.get('TP2','-')}
🎯 TP3: {tps.get('TP3','-')}
🎯 TP4: {tps.get('TP4','-')}
🛑 סטופלוס: {stop}

📊 חיווי TradingView: {tv_summary['RECOMMENDATION']}
BUY: {tv_summary['BUY']} | SELL: {tv_summary['SELL']} | NEUTRAL: {tv_summary['NEUTRAL']}
"""
    return text, chart

def send_update(symbols):
    for s in symbols:
        text, chart = analyze_coin(s)
        bot.send_message(chat_id=CHAT_ID, text=text)
        bot.send_photo(chat_id=CHAT_ID, photo=open(chart, "rb"))

if __name__ == "__main__":
    # לדוגמה נבדוק 2 מטבעות
    send_update(["BTC", "ETH"])
  
