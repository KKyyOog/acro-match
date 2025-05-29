from flask import Blueprint, request
import json
import os
import sys
import re
from utils.sheets import add_user_id_mapping_if_new, update_birthday_if_exists

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
                send_line_message(user_id, "友だち追加ありがとうございます！お名前と生年月日(〇〇〇〇年〇〇月〇〇日)を送ってください。")

            elif event_type == "message":
                user_message = event.get("message", {}).get("text", "")

                # 生年月日形式かを判定
                if re.match(r"^\d{4}年\d{1,2}月\d{1,2}日$", user_message):
                    updated = update_birthday_if_exists(user_id, user_message)
                    if updated:
                        send_line_message(user_id, f"生年月日 {user_message} を登録しました。")
                    else:
                        send_line_message(user_id, "先にお名前を送ってください。")
                else:
                    # 名前として処理
                    add_user_id_mapping_if_new(webhook_id=user_id, name=user_message)
                    send_line_message(user_id, f"{user_message} さん、登録ありがとうございます！")

        return "OK", 200
    except Exception as e:
        import traceback
        print("❌ Webhook処理エラー:\n", traceback.format_exc())
        return "Error", 500
