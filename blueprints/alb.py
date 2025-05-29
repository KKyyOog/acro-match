# 修正後の alb.py
from flask import Blueprint, request, render_template
from utils.sheets import get_sheet, load_settings, get_webhook_id_from_liff_id
from utils.liff import get_liff_id

alb_bp = Blueprint('alb', __name__)

@alb_bp.route("/register_alb")
def register_alb():
    settings = load_settings()
    liff_id = get_liff_id("alb")
    return render_template("form_alb.html", settings=settings, liff_id=liff_id)

@alb_bp.route("/submit_alb", methods=["POST"])
def submit_alb():
    try:
        settings = load_settings()
        sheet = get_sheet("アルバイト登録シート")

        # LIFF ID -> Webhook ID 変換
        liff_user_id = request.form.get("user_id", "")
        true_user_id = get_webhook_id_from_liff_id(liff_user_id) or liff_user_id

        # ヘッダーを更新
        sheet.delete_rows(1)
        headers = [
            settings.get("form_label_name", "名前"),
            settings.get("form_label_alb_experience", "経験"),
            settings.get("form_label_area", "希望エリア"),
            settings.get("form_label_available", "稼働可能日・時間"),
            settings.get("form_label_reachtime", "連絡可能時間帯")
        ]
        for field in settings.get("custom_fields", []):
            headers.append(field.get("label", ""))
        headers.append("user_id")
        sheet.insert_row(headers, index=1)

        # フォームデータ取得
        name = request.form.get("name", "")
        experience_list = request.form.getlist("experience")
        experience_str = ", ".join(experience_list)
        area = request.form.get("area", "")
        available = request.form.get("available", "")
        reachtime = request.form.get("reachtime", "")

        custom_values = [request.form.get(field.get("name", ""), "") for field in settings.get("custom_fields", [])]

        row = [name, experience_str, area, available, reachtime] + custom_values + [true_user_id]
        sheet.append_row(row)

        return "登録が完了しました！"
    except Exception as e:
        print(f"submit_alb エラー: {e}")
        return "Internal Server Error", 500