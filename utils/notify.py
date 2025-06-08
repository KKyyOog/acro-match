# utils/notify.py

import os
import requests
from dotenv import load_dotenv
from utils.logging_util import log_exception
from typing import Tuple, Optional

load_dotenv()

LINE_API_URL = "https://api.line.me/v2/bot/message/push"
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

def send_line_message(user_id: str, message_text: str) -> Tuple[bool, Optional[str]]:
    access_token = os.getenv("LINE_ACCESS_TOKEN")
    print("🪪 LINE_ACCESS_TOKEN:", access_token is not None)

    url = LINE_API_URL
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
            return False, f"LINE送信失敗: {response.status_code} {response.text}"

        return True, None

    except Exception as e:
        log_exception(e, context="send_line_message 内で例外")
        return False, str(e)
