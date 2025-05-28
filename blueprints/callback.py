from flask import Blueprint, request
import json
import os
import sys
from utils.sheets import add_user_with_name_if_new


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.notify import send_line_message

callback_bp = Blueprint("callback", __name__)

@callback_bp.route("/callback", methods=["POST"])
def callback():
    try:
        data = request.get_json(force=True)
        events = data.get("events", [])

        for event in events:
            user_id = event.get("source", {}).get("userId")
            event_type = event.get("type")

            if not user_id:
                continue

            if event_type == "follow":
                send_line_message(user_id, "友だち追加ありがとうございます！お名前を送ってください。")

            elif event_type == "message":
                user_message = event.get("message", {}).get("text", "")
                add_user_with_name_if_new(user_id, user_message)
                send_line_message(user_id, f"{user_message} さん、登録ありがとうございます！")

        return "OK", 200
    except Exception as e:
        import traceback
        print("❌ Webhook処理エラー:\n", traceback.format_exc())
        return "Error", 500