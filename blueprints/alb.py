from flask import Blueprint, request, render_template
from utils.sheets import get_sheet, load_settings

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
        name = request.form.get('name')
        gym = request.form.get('gym')
        cheer = request.form.get('cheer')
        area = request.form.get('area')
        available = request.form.get('available')
        user_id = request.form.get('user_id')

        custom_values = [
            request.form.get(field.get("name", ""), "")
            for field in settings.get("custom_fields", [])
        ]

        sheet = get_sheet("アルバイト登録シート")
        row = [name, gym, cheer, area, available, user_id] + custom_values
        sheet.append_row(row)

        return "登録が完了しました！"
    except Exception as e:
        print(f"submit_alb エラー: {e}")
        return "Internal Server Error", 500
