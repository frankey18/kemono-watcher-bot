from flask import Flask
import os
import requests
from bs4 import BeautifulSoup
import threading
import time

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

CHECK_URL = "https://kemono.cr/artists?q=ai_oma&service=patreon&sort_by=updated&order="
TARGET_CREATOR = "AI_Omaga"
last_update = ""

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_USER_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("❌ Telegram 發送失敗:", e)

def check_update():
    global last_update
    while True:
        try:
            print("🔍 檢查更新中...")
            res = requests.get(CHECK_URL)
            soup = BeautifulSoup(res.text, "html.parser")
            cards = soup.select("div.card--user")

            found = False

            for card in cards:
                name_tag = card.select_one(".user-card__name")
                if name_tag and name_tag.text.strip() == TARGET_CREATOR:
                    time_tag = card.select_one(".user-card__updated time")
                    if time_tag and time_tag.has_attr("datetime"):
                        current_update = time_tag["datetime"]
                        print(f"📅 {TARGET_CREATOR} 最新更新時間：{current_update}")

                        if current_update != last_update:
                            send_telegram_message(f"🆕 {TARGET_CREATOR} 有新更新囉！\n{CHECK_URL}")
                            last_update = current_update
                        else:
                            print("⏸ 沒有更新。")
                        found = True
                    break

            if not found:
                print(f"⚠️ 沒有找到創作者：{TARGET_CREATOR}")

        except Exception as e:
            print("❌ 檢查時出錯：", e)

        time.sleep(600)  # 每 10 分鐘檢查一次

@app.route("/")
def home():
    return "✅ Kemono Watcher is running."

if __name__ == "__main__":
    send_telegram_message("📣 AI_Omaga 監控啟動成功，開始檢查更新。")
    threading.Thread(target=check_update).start()
    app.run(host="0.0.0.0", port=8000)
