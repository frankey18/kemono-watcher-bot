from flask import Flask
import os
import requests
from bs4 import BeautifulSoup
import threading
import time

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_USER_ID = os.getenv("TELEGRAM_USER_ID")

CHECK_URL = "https://kemono.cr/patreon/user/135474437"
last_content = ""

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_USER_ID, "text": message}
    requests.post(url, data=payload)

def check_update():
    global last_content
    while True:
        try:
            res = requests.get(CHECK_URL)
            soup = BeautifulSoup(res.text, "html.parser")
            new_content = soup.get_text(strip=True)[:500]  # 抓前段內容比較
            if new_content != last_content:
                send_telegram_message("🚨 Kemono 網頁有更新囉！")
                last_content = new_content
            else:
                print("✅ 無更新")
        except Exception as e:
            print("❌ 發生錯誤：", e)
        time.sleep(600)  # 每 10 分鐘檢查一次

@app.route("/")
def home():
    return "✅ Kemono Watcher is running."

if __name__ == "__main__":
    threading.Thread(target=check_update).start()
    app.run(host="0.0.0.0", port=8000)

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_USER_ID:
    raise ValueError("⚠️ TELEGRAM_BOT_TOKEN 或 USER_ID 未設定")
