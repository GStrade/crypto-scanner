from telegram import Bot
from config import TOKEN, CHAT_ID
from analysis import get_tv_analysis, calculate_fibonacci_tps, get_trending_coins
from charting import generate_chart
from pycoingecko import CoinGeckoAPI
import yfinance as yf
import sys

if not TOKEN or not CHAT_ID:
    print("❌ שגיאה: BOT_TOKEN או CHAT_ID לא מוגדרים")
    sys.exit(1)

bot = Bot(token=TOKEN)
cg = CoinGeckoAPI()

def get_top_coins(limit=100):
    return cg.get_coins_markets(
        vs_currency="usd",
        order="market_cap_desc",
        per_page=limit,
        page=1
    )

def analyze_coin(coin, trending_list):
    symbol = coin["symbol"].upper()
    try:
        data = yf.Ticker(symbol + "-USD").history(period="3mo")
        if data.empty:
            return None, None

        entry = round(data["Close"].iloc[-1], 4)
        tv_summary = get_tv_analysis(symbol)

        # קריטריונים
        if tv_summary["RECOMMENDATION"] not in ["BUY", "STRONG_BUY"]:
            return None, None
        if coin["price_change_percentage_24h"] <= 0:
            return None, None
        if coin["market_cap"] < 50_000_000:
            return None, None
        if coin["total_volume"] < coin["market_cap"] * 0.01:
            return None, None

        tps = calculate_fibonacci_tps(data["Close"].tolist(), entry)
        stop = round(entry * 0.9, 4)
        chart = generate_chart(symbol, entry, stop, tps)

        trending_text = "🔥 המטבע בטופ טרנדינג ברשתות" if symbol in trending_list else ""

        text = f"""
📊 {symbol} (BINANCE)
💵 מחיר כניסה: {entry}
🎯 TP1: {tps.get('TP1','-')}
🎯 TP2: {tps.get('TP2','-')}
🎯 TP3: {tps.get('TP3','-')}
🎯 TP4: {tps.get('TP4','-')}
🛑 סטופלוס: {stop}

📊 TradingView: {tv_summary['RECOMMENDATION']}
BUY: {tv_summary['BUY']} | SELL: {tv_summary['SELL']} | NEUTRAL: {tv_summary['NEUTRAL']}

📈 שינוי 24h: {round(coin['price_change_percentage_24h'],2)}%
💰 שווי שוק: ${coin['market_cap']:,}
🔊 ווליום יומי: ${coin['total_volume']:,}

{trending_text}
"""
        return text, chart
    except Exception as e:
        print(f"שגיאה במטבע {symbol}: {e}")
        return None, None

def send_update():
    all_coins = get_top_coins(100)
    trending_list = get_trending_coins(50)
    selected = []

    for coin in all_coins:
        text, chart = analyze_coin(coin, trending_list)
        if text:
            selected.append((coin["symbol"], text, chart))

    best = selected[:5]

    if not best:
        bot.send_message(chat_id=CHAT_ID, text="⚠️ לא נמצאו מטבעות מתאימים היום.")
        return

    bot.send_message(chat_id=CHAT_ID, text=f"🚀 סריקת קריפטו יומית ({len(best)} מטבעות):")
    for _, text, chart in best:
        bot.send_message(chat_id=CHAT_ID, text=text)
        bot.send_photo(chat_id=CHAT_ID, photo=open(chart, "rb"))

if __name__ == "__main__":
    send_update()
