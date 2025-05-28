from flask import Blueprint, request
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.notify import send_line_message

callback_bp = Blueprint("callback", __name__)

@callback_bp.route("/callback", methods=["POST"])
def callback():
    try:
        body = request.get_json()
        print("📩 Webhook受信:", body)
        events = body.get("events", [])
        for event in events:
            if event.get("type") == "follow":
                user_id = event["source"]["userId"]
                print("✅ 新規フォローユーザーID:", user_id)
                send_line_message(user_id, "友だち追加ありがとうございます！早速募集一覧で募集を探してみましょう！")
        return "OK"
    except Exception as e:
        import traceback
        print("❌ Webhook処理エラー:\n", traceback.format_exc())
        return "Error", 500

