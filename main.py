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

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_USER_ID:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN 或 TELEGRAM_USER_ID 未設定")

last_content = ""

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_USER_ID, "text": message}
    try:
        res = requests.post(url, data=payload)
        print("📨 發送通知結果：", res.status_code, res.text)
    except Exception as e:
        print("❌ 發送通知失敗：", e)

def check_update():
    global last_content
    while True:
        try:
            res = requests.get(CHECK_URL)
            soup = BeautifulSoup(res.text, "html.parser")

            # 抓取整頁前段內容作為比較依據
            main_area = soup.find("main")
            new_content = (main_area.get_text(strip=True) if main_area else soup.get_text(strip=True))[:500]

            if new_content != last_content:
                print("🔔 發現新內容，發送通知...")
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
    threading.Thread(target=check_update, daemon=True).start()
    port = int(os.environ.get("PORT", 8000))  # 取用 Render 指定的 PORT
    app.run(host="0.0.0.0", port=port)

