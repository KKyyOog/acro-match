# blueprints/callback.py
from flask import Blueprint, request, jsonify
import re
from utils.user import register_user_info
from utils.sheets import update_birthday_if_exists
from utils.notify import send_line_message
from utils.logging_util import log_exception

callback_bp = Blueprint("callback", __name__)

@callback_bp.route("/callback", methods=["POST"])
def handle_callback():
    data = request.get_json(silent=True) or {}
    print("\U0001F4E9 Webhook受信:", data)
    return "OK", 200

@callback_bp.route("", methods=["POST"])
def receive_callback():
    try:
        data = request.get_json(force=True)
        print("\U0001F4E9 Webhook受信:", data)
        events = data.get("events", [])

        for event in events:
            user_id = event.get("source", {}).get("userId")
            webhook_id = event.get("webhookEventId")
            if not user_id:
                continue

            if event.get("type") == "follow":
                send_line_message(user_id, "友だち追加ありがとうございます！\nまずお名前を送ってください。その後、生年月日（〇〇〇〇年〇〇月〇〇日）を送ってください。")

            elif event.get("type") == "message":
                msg = event.get("message", {}).get("text", "")

                if '\n' in msg:
                    parts = msg.split('\n')
                    if len(parts) >= 2:
                        name, bday = parts[0].strip(), parts[1].strip()
                        if re.match(r"^\d{4}年\d{1,2}月\d{1,2}日$", bday):
                            register_user_info(name, bday, user_id, webhook_event_id=webhook_id)
                            send_line_message(user_id, f"{name} さん、登録ありがとうございます！\n生年月日 {bday} も登録しました。")
                            continue

                if re.match(r"^\d{4}年\d{1,2}月\d{1,2}日$", msg):
                    updated = update_birthday_if_exists(user_id, msg)
                    send_line_message(user_id, f"生年月日 {msg} を登録しました。" if updated else "先にお名前を送ってください。")
                else:
                    register_user_info(msg, "", user_id, webhook_event_id=webhook_id)
                    send_line_message(user_id, f"{msg} さん、登録ありがとうございます！")

        return "OK", 200
    except Exception as e:
        log_exception(e, context="LINE Callback 処理")
        return "Error", 500

@callback_bp.route("/interest", methods=["POST"])
def receive_interest():
    try:
        print("\U0001F4E8 興味あり受信:", request.json)
        return jsonify({"message": "受信OK"}), 200
    except Exception as e:
        log_exception(e, context="Callback /interest 処理")
        return "Error", 500