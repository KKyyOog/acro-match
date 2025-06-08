# blueprints/callback.py
from flask import Blueprint, request, jsonify
import re
from utils.user import register_user_info
from utils.notify import send_line_message
from utils.logging_util import log_exception
from datetime import datetime

callback_bp = Blueprint("callback", __name__)

# 🧠 ユーザーごとの一時状態保存（名前）
user_states = {}  # user_id → {'name': str}

@callback_bp.route("/callback", methods=["POST"])
def handle_callback():
    data = request.get_json(silent=True) or {}
    print("📩 Webhook受信:", data)
    return "OK", 200

@callback_bp.route("", methods=["POST"])
def receive_callback():
    try:
        data = request.get_json(force=True)
        print("📩 Webhook受信:", data)
        events = data.get("events", [])

        for event in events:
            user_id = event.get("source", {}).get("userId")
            if not user_id:
                continue

            if event.get("type") == "follow":
                send_line_message(user_id, "友だち追加ありがとうございます！\nまずお名前を送ってください。その後、生年月日（○○○○年○○月○○日）を送ってください。")

            elif event.get("type") == "message":
                msg = event.get("message", {}).get("text", "").strip()

                # 名前\n誕生日 の同時送信パターン
                if '\n' in msg:
                    parts = msg.split('\n')
                    if len(parts) >= 2:
                        name, bday = parts[0].strip(), parts[1].strip()
                        if re.match(r"^\d{4}年\d{1,2}月\d{1,2}日$", bday):
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            register_user_info(name, bday, chat_liff_id=user_id)
                            send_line_message(user_id, f"{name} さん、登録ありがとうございます！\n生年月日 {bday} も登録しました。")
                            user_states[user_id] = {'name': name}
                            continue

                # 生年月日単独パターン
                if re.match(r"^\d{4}年\d{1,2}月\d{1,2}日$", msg):
                    name = user_states.get(user_id, {}).get("name")
                    if name:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        register_user_info(name, msg, chat_liff_id=user_id)
                        send_line_message(user_id, f"{name} さん、誕生日 {msg} を登録しました！")
                    else:
                        send_line_message(user_id, "先にお名前を送ってください。")
                    continue

                # 名前だけ送られたと判断
                user_states[user_id] = {'name': msg}
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                register_user_info(msg, "", chat_liff_id=user_id)
                send_line_message(user_id, f"{msg} さん、登録ありがとうございます！\n次に誕生日（○○○○年○○月○○日）を送ってください。")

        return "OK", 200
    except Exception as e:
        log_exception(e, context="LINE Callback 処理")
        return "Error", 500

@callback_bp.route("/interest", methods=["POST"])
def receive_interest():
    try:
        print("📨 興味あり受信:", request.json)
        return jsonify({"message": "受信OK"}), 200
    except Exception as e:
        log_exception(e, context="Callback /interest 処理")
        return "Error", 500
