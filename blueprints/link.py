# blueprints/link.py
from flask import Blueprint, request
from utils.user import register_user_info
from utils.sheets import append_row_if_new_user
from datetime import datetime

link_bp = Blueprint("link", __name__)

@link_bp.route("/alb/submit", methods=["POST"])
def submit():
    try:
        data = request.get_json()
        print("📩 アルバイト登録データ受信:", data)

        name = data.get("name")
        birthday4 = data.get("birthday4")
        user_id = data.get("userId")  # ← アプリの LIFF ID

        birthday_full = f"2000年{birthday4[:2]}月{birthday4[2:]}日" if len(birthday4) == 4 else ""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        register_user_info(name, birthday_full, app_liff_id=user_id)

        # ログ保存（アルバイト登録シート）
        append_row_if_new_user("アルバイト登録", [name, birthday4, user_id, timestamp])
        return "OK", 200

    except Exception as e:
        print("❌ エラー:", e)
        return "Error", 500
