import os
import requests
import yfinance as yf
import matplotlib.pyplot as plt
from pycoingecko import CoinGeckoAPI
from telegram import Bot

# --- קריאת משתני סביבה ---
TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
LUNAR_API_KEY = os.environ.get("LUNAR_API_KEY")

bot = Bot(token=TOKEN)
cg = CoinGeckoAPI()

# ---------------- פונקציות עזר ----------------
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

def get_top_lowcaps():
    coins = cg.get_coins_markets(vs_currency='usd', order='market_cap_asc', per_page=100, page=1)
    filtered = []
    for c in coins:
        if not c['market_cap']:
            continue
        if c['market_cap'] > 50_000_000:   # Low Cap
            continue
        if c['current_price'] > 5:         # מחיר מתחת ל-5$
            continue
        if c['total_volume'] < c['market_cap'] * 0.1:  # ווליום חריג
            continue
        if c['price_change_percentage_24h'] and c['price_change_percentage_24h'] < 5:
            continue
        filtered.append(c)
    return filtered[:5]

def get_trending_coins():
    trending = cg.get_search_trending()
    results = []
    for coin in trending['coins']:
        item = coin['item']
        results.append({
            'id': item['id'],
            'name': item['name'],
            'symbol': item['symbol'],
            'market_cap_rank': item['market_cap_rank'],
            'score': item['score']
        })
    return results[:5]

def get_lunar_trending():
    url = "https://lunarcrush.com/api4/public/coins/list/v1"
    params = {"limit": 10, "sort": "social_volume_24h", "desc": True}
    headers = {"Authorization": f"Bearer {LUNAR_API_KEY}"}
    r = requests.get(url, headers=headers)
    data = r.json()
    return data.get("data", [])[:5]

# ---------------- שליחת דוח ----------------
def send_report():
    bot.send_message(chat_id=CHAT_ID, text="🚀 סורק הקריפטו הופעל בהצלחה!")

    coins = get_top_lowcaps()
    message = "📊 *דו\"ח מטבעות יומי – קריפטו/אלטקוין*\n\n"

    if not coins:
        message += "❌ לא נמצאו Low Cap מטבעות מתאימים היום.\n\n"
    else:
        for coin in coins:
            message += f"💎 *{coin['name']}* ({coin['symbol'].upper()})\n"
            message += f"💰 שווי שוק: {coin['market_cap']:,}$\n"
            message += f"💵 מחיר: {coin['current_price']}$\n"
            message += f"📈 שינוי 24ש': {coin['price_change_percentage_24h']}%\n\n"

    trending = get_trending_coins()
    if trending:
        hot_list = "\n".join([f"🔥 {c['name']} ({c['symbol'].upper()})" for c in trending])
        message += f"🔥 המטבעות הכי חמים ב-CoinGecko:\n{hot_list}\n\n"

    lunar = get_lunar_trending()
    if lunar:
        message += "🌐 המטבעות הכי מדוברים ברשתות (LunarCrush):\n"
        for c in lunar:
            message += f"🔥 {c['name']} ({c['symbol']}) | אזכורים: {c.get('social_volume_24h','?')} | GalaxyScore: {c.get('galaxy_score','?')}\n"

    bot.send_message(chat_id=CHAT_ID, text=message, parse_mode="Markdown")

    # שליחת גרפים
    for coin in coins:
        chart_path = generate_chart(coin['symbol'])
        if chart_path:
            bot.send_photo(chat_id=CHAT_ID, photo=open(chart_path, 'rb'), caption=f"{coin['symbol'].upper()} – גרף יומי")

    bot.send_message(chat_id=CHAT_ID, text="✅ סריקת הקריפטו הסתיימה")

if __name__ == "__main__":
    send_report()
