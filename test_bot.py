from telegram import Bot
from config import TOKEN, CHAT_ID
from analysis import get_trending_coins

bot = Bot(token=TOKEN)

def test_trending():
    trending = get_trending_coins(10)
    msg = "🔥 רשימת מטבעות טרנדיים מ-LunarCrush:\n" + ", ".join(trending)
    print(msg)
    bot.send_message(chat_id=CHAT_ID, text=msg)

if __name__ == "__main__":
    test_trending()
