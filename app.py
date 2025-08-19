import requests
import yfinance as yf
import matplotlib.pyplot as plt
from pycoingecko import CoinGeckoAPI
from telegram import Bot

# --- Bot Token and Chat ID ---
bot = Bot("8446143029:AAH1t5c-4RsTwLE6elOqpRJ6_jlzAkF8Z0U")
chat_id = "1715673393"

cg = CoinGeckoAPI()

def get_top_lowcaps():
    coins = cg.get_coins_markets(vs_currency='usd', order='market_cap_asc', per_page=50, page=1)
    low_caps = [c for c in coins if c['market_cap'] and c['market_cap'] < 50_000_000]
    hot_coins = [c for c in low_caps if c['total_volume'] > c['market_cap'] * 0.1]
    return hot_coins[:5]

def send_report():
    coins = get_top_lowcaps()
    for coin in coins:
        ticker = coin['symbol'].upper() + "-USD"
        try:
            data = yf.download(ticker, period="1mo", interval="1d")
            if data.empty:
                continue

            plt.figure(figsize=(8,4))
            plt.plot(data['Close'])
            plt.title(f"{coin['name']} ({coin['symbol'].upper()})")
            plt.savefig("chart.png")

            msg = f"""
🚀 {coin['name']} ({coin['symbol'].upper()})
💰 שווי שוק: {coin['market_cap']:,}$
📈 ווליום: {coin['total_volume']:,}$
🔎 סיבה: ווליום חריג
💡 עסקה מוצעת: לונג
"""
            bot.send_message(chat_id, msg)
            bot.send_photo(chat_id, photo=open("chart.png","rb"))
        except Exception as e:
            print("Error with", coin['name'], e)

if __name__ == "__main__":
    send_report()
