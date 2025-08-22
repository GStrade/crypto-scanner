import os
import requests
import yfinance as yf
import matplotlib.pyplot as plt
from pycoingecko import CoinGeckoAPI
from telegram import Bot

# --- Secrets ---
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
CRYPTOCOMPARE_KEY = os.environ.get("CRYPTOCOMPARE_KEY")

bot = Bot(token=TOKEN)
cg = CoinGeckoAPI()

def generate_chart(symbol):
    try:
        data = yf.download(symbol + "-USD", period="6mo", interval="1d")
        if data.empty:
            return None
        plt.figure(figsize=(8,4))
        plt.plot(data.index, data['Close'])
        plt.title(f"{symbol.upper()} – גרף יומי")
        plt.xlabel("תאריך")
        plt.ylabel("מחיר ($)")
        filepath = f"{symbol}.png"
        plt.savefig(filepath)
        plt.close()
        return filepath
    except Exception as e:
        print(f"שגיאה בגרף עבור {symbol}: {e}")
        return None

def get_lowcaps():
    coins = cg.get_coins_markets(vs_currency='usd', order='market_cap_asc', per_page=50, page=1)
    filtered = []
    for c in coins:
        if not c['market_cap'] or c['market_cap'] > 50_000_000:
            continue
        if c['current_price'] > 5:
            continue
        filtered.append(c)
    return filtered[:5]

def get_binance_price(symbol):
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol.upper()}USDT"
    try:
        r = requests.get(url)
        data = r.json()
        return {
            "price": float(data['lastPrice']),
            "change": float(data['priceChangePercent']),
            "volume": float(data['quoteVolume'])
        }
    except:
        return None

def get_cryptocompare_news():
    url = f"https://min-api.cryptocompare.com/data/v2/news/?lang=EN&api_key={CRYPTOCOMPARE_KEY}"
    r = requests.get(url)
    data = r.json()
    return data.get("Data", [])[:5]

def send_report():
    bot.send_message(chat_id=CHAT_ID, text="🚀 סורק הקריפטו (Multi-Source) הופעל בהצלחה!")

    coins = get_lowcaps()
    if not coins:
        bot.send_message(chat_id=CHAT_ID, text="❌ לא נמצאו מטבעות מתאימים היום.")
        return

    news = get_cryptocompare_news()
    headlines = "\n".join([f"📰 {n['title']}" for n in news])

    message = "📊 *דו\"ח מטבעות יומי – קריפטו/אלטקוין*\n\n"
    for coin in coins:
        name = coin['name']
        symbol = coin['symbol'].upper()
        mcap = coin['market_cap']

        binance = get_binance_price(symbol)
        if not binance:
            continue
        price = binance['price']
        change = binance['change']
        volume = binance['volume']

        direction = "לונג" if change > 0 else "שורט"
        entry = round(price * 0.98, 4)
        stop = round(price * 0.90, 4)
        tp1 = round(price * 1.15, 4)
        tp2 = round(price * 1.30, 4)

        message += f"**{name} ({symbol})** — Rank {coin.get('market_cap_rank','?')}\n"
        message += f"מחיר נוכחי: ${price}\n"
        message += f"כיוון: {direction}\n"
        message += f"סיבה: "
        if abs(change) > 5: message += "📈 שינוי יומי חד | "
        if volume > mcap * 0.1: message += "🔥 ווליום חריג | "
        message += f"💰 שווי שוק: {mcap:,}$\n"
        message += f"כניסה: ${entry} (הדרגתי)\n"
        message += f"סטופ: ${stop}\n"
        message += f"יעדים: TP1 ${tp1} (+15%) | TP2 ${tp2} (+30%)\n"
        message += f"הערכת סיכוי: ~{round(abs(change),2)}%\n\n"

    message += "📰 *חדשות אחרונות מ-CryptoCompare:*\n" + headlines
    message += "\n\n*הערה*: לא ייעוץ השקעות. שימוש לשיקולך בלבד."

    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

    for coin in coins:
        chart_path = generate_chart(coin['symbol'])
        if chart_path:
            bot.send_photo(chat_id=CHAT_ID, photo=open(chart_path, 'rb'), caption=f"{coin['symbol'].upper()} – גרף יומי")

    bot.send_message(chat_id=CHAT_ID, text="✅ סריקת הקריפטו הסתיימה")

if __name__ == "__main__":
    send_report()
