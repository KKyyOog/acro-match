from flask import Blueprint, request
import json
from utils.notify import send_line_message
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.notify import send_line_message


callback_bp = Blueprint("callback", __name__)

@callback_bp.route("/callback", methods=["POST"])
def callback():
    body = request.get_data(as_text=True)
    print("📩 Webhook受信:", body)
    try:
        events = json.loads(body).get("events", [])
        for event in events:
            if event.get("type") == "follow":
                user_id = event["source"]["userId"]
                print("✅ 新規フォローユーザーID:", user_id)
                send_line_message(user_id, "友だち追加ありがとうございます！")
        return "OK"
    except Exception as e:
        print("❌ Webhook処理エラー:", e)
        return "Error", 500

success = send_line_message(user_id, "友だち追加ありがとうございます！")
print("📤 通知送信成功？", success)
