from flask import Blueprint, request
import json
import os
import sys
import re
from utils.sheets import add_user_id_mapping_if_new, update_birthday_if_exists
from utils.notify import notify_classroom_of_interest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.notify import send_line_message

callback_bp = Blueprint("callback", __name__)

user_state = {}  # 例： {user_id: {'step': 'awaiting_birthday', 'name': '山田太郎'}}

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
                send_line_message(user_id, "友だち追加ありがとうございます！\nまずお名前を送ってください。その後、生年月日（〇〇〇〇年〇〇月〇〇日）を送ってください。")

            elif event_type == "message":
                user_message = event.get("message", {}).get("text", "")

                # 改行を含む場合：名前＋生年月日の両方が送られてきた可能性
                if '\n' in user_message:
                    parts = user_message.split('\n')
                    if len(parts) >= 2:
                        name_candidate = parts[0]
                        birthday_candidate = parts[1]
                        if re.match(r"^\d{4}年\d{1,2}月\d{1,2}日$", birthday_candidate):
                            add_user_id_mapping_if_new(webhook_id=user_id, name=name_candidate)
                            update_birthday_if_exists(user_id, birthday_candidate)
                            send_line_message(user_id, f"{name_candidate} さん、登録ありがとうございます！\n生年月日 {birthday_candidate} も登録しました。")
                            continue  # 次のイベントへ

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


