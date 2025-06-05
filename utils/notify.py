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
    """
    LINEメッセージ送信処理。
    成功時: (True, None)
    失敗時: (False, エラーメッセージ)
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message_text}]
    }
    print("送信ペイロード:", payload)
    try:
        response = requests.post(LINE_API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            error_info = f"LINE通知失敗: {response.status_code} - {response.text}"
            print("⚠️", error_info)
            return False, error_info
        print("✅ 通知送信成功")
        return True, None
    except Exception as e:
        log_exception(e, context="LINE通知送信エラー")
        return False, str(e)

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
