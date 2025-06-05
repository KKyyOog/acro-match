# utils/notify.py

import os
import requests
from dotenv import load_dotenv
from utils.sheets import get_webhook_id_from_liff_id
from utils.logging_util import log_exception

load_dotenv()

LINE_API_URL = "https://api.line.me/v2/bot/message/push"
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

def send_line_message(user_id, message_text):
    access_token = os.getenv("LINE_ACCESS_TOKEN")
    print("🪪 LINE_ACCESS_TOKEN:", access_token is not None)

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message_text}]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print("📨 LINE送信ステータス:", response.status_code)
        print("📨 レスポンス内容:", response.text)

        if response.status_code != 200:
            raise Exception(f"LINE送信失敗: {response.status_code} {response.text}")

    except Exception as e:
        print("❌ send_line_message 内で例外:", e)


def notify_classroom_of_interest(liff_id, interested_user_name="誰かが"):
    """
    LIFF ID に紐づく教室ユーザーに「興味あり」通知を送信。
    """
    try:
        webhook_id = get_webhook_id_from_liff_id(liff_id)
        if webhook_id:
            message = f"{interested_user_name} あなたの募集に興味を持っています！"
            success, err = send_line_message(webhook_id, message)
            return success
        else:
            print("❌ 対応するWebhook IDが見つかりません")
            return False
    except Exception as e:
        log_exception(e, context="教室側通知処理")
        return False
