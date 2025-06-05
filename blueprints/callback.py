# blueprints/callback.py

from flask import Blueprint, request, jsonify
import re
from utils.user import register_user_info
from utils.sheets import update_birthday_if_exists
from utils.notify import send_line_message
from utils.logging_util import log_exception

callback_bp = Blueprint("callback", __name__, url_prefix="/callback")

user_state = {}  # 例： {user_id: {'step': 'awaiting_birthday', 'name': '山田太郎'}}

@callback_bp.route("/", methods=["POST"])
def receive_callback():
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

                # 改行がある場合（名前と誕生日の同時送信）
                if '\n' in user_message:
                    parts = user_message.split('\n')
                    if len(parts) >= 2:
                        name_candidate = parts[0].strip()
                        birthday_candidate = parts[1].strip()
                        if re.match(r"^\d{4}年\d{1,2}月\d{1,2}日$", birthday_candidate):
                            register_user_info(name_candidate, birthday_candidate, user_id)
                            send_line_message(user_id, f"{name_candidate} さん、登録ありがとうございます！\n生年月日 {birthday_candidate} も登録しました。")
                            continue  # 次のイベントへ

                # 生年月日のみ送られてきた場合
                if re.match(r"^\d{4}年\d{1,2}月\d{1,2}日$", user_message):
                    updated = update_birthday_if_exists(user_id, user_message)
                    if updated:
                        send_line_message(user_id, f"生年月日 {user_message} を登録しました。")
                    else:
                        send_line_message(user_id, "先にお名前を送ってください。")
                else:
                    # 名前として処理
                    register_user_info(user_message, "", user_id)
                    send_line_message(user_id, f"{user_message} さん、登録ありがとうございます！")

        return "OK", 200

    except Exception as e:
        log_exception(e, context="LINE Callback 処理")
        return "Error", 500

@callback_bp.route("/interest", methods=["POST"])
def receive_interest():
    try:
        data = request.json
        print("📨 興味あり受信:", data)
        return jsonify({"message": "受信OK"}), 200
    except Exception as e:
        log_exception(e, context="Callback /interest 処理")
        return "Error", 500
