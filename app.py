import requests
import yfinance as yf
import matplotlib.pyplot as plt
from pycoingecko import CoinGeckoAPI
from telegram import Bot

# --- Bot Token & Chat ID ---
bot = Bot("8446143029:AAH1t5c-4RsTwLE6elOqpRJ6_jlzAkF8Z0U")
chat_id = "1715673393"

# --- LunarCrush API Key ---
LUNAR_API_KEY = "xsnjnf4qtqa704izrqzale17lrmejlr9b3tk4a7hc"

cg = CoinGeckoAPI()

# ---------------- CoinGecko Screener ----------------
def get_top_lowcaps():
    coins = cg.get_coins_markets(vs_currency='usd', order='market_cap_asc', per_page=100, page=1)
    filtered = []
    for c in coins:
        if not c['market_cap']:
            continue
        if c['market_cap'] > 50_000_000:   # שווי שוק קטן
            continue
        if c['current_price'] > 5:         # מחיר קטן מ-5$
            continue
        if c['total_volume'] < c['market_cap'] * 0.1:  # ווליום חריג
            continue
        if c['price_change_percentage_24h'] and c['price_change_percentage_24h'] < 5: # עלייה יומית
            continue
        filtered.append(c)
    return filtered[:5]

# ---------------- CoinGecko Trending ----------------
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
    return results

# ---------------- LunarCrush Trending ----------------
def get_lunar_trending():
    url = "https://lunarcrush.com/api4/public/coins/list/v1"
    params = {"limit": 10, "sort": "social_volume_24h", "desc": True}
    headers = {"Authorization": f"Bearer {LUNAR_API_KEY}"}
    r = requests.get(url, headers=headers)
    data = r.json()
    return data.get("data", [])[:5]

# ---------------- Send Report ----------------
def send_report():
    # בדיקה שהבוט מחובר
    bot.send_message(chat_id, "🚀 סורק הקריפטו התחיל להריץ!")

    # CoinGecko LowCap Filter
    coins = get_top_lowcaps()
    if not coins:
        bot.send_message(chat_id, "❌ לא נמצאו מטבעות מסוננים היום.")
    else:
        for coin in coins:
            msg = f"""
💎 {coin['name']} ({coin['symbol'].upper()})
💰 שווי שוק: {coin['market_cap']:,}$
💵 מחיר: {coin['current_price']}$
📈 שינוי 24ש': {coin['price_change_percentage_24h']}%
"""
            bot.send_message(chat_id, msg)

    # CoinGecko Trending
    trending = get_trending_coins()
    hot_list = "\n".join([f"{c['name']} ({c['symbol'].upper()})" for c in trending[:5]])
    bot.send_message(chat_id, f"🔥 המטבעות הכי חמים ב-CoinGecko:\n{hot_list}")

    # LunarCrush Trending
    lunar = get_lunar_trending()
    if lunar:
        msg = "🌐 המטבעות הכי מדוברים ברשתות (LunarCrush):\n"
        for c in lunar:
            msg += f"🔥 {c['name']} ({c['symbol']}) | אזכורים: {c.get('social_volume_24h','?')} | GalaxyScore: {c.get('galaxy_score','?')}\n"
        bot.send_message(chat_id, msg)
    else:
        bot.send_message(chat_id, "⚠️ לא התקבלו נתונים מ-LunarCrush.")

if __name__ == "__main__":
    send_report()
