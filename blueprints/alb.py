# blueprints/alb.py
from flask import Blueprint, request, render_template, redirect
from utils.sheets import get_sheet
from utils.settings import load_settings
from utils.liff import get_liff_id
from utils.user import register_user_info
from utils.logging_util import log_exception
from flask_wtf.csrf import generate_csrf

alb_bp = Blueprint("alb", __name__, url_prefix="/alb")

@alb_bp.route("/register", methods=["GET"])
def show_register_form():
    try:
        return render_template("form_alb.html", settings=load_settings(), liff_id=get_liff_id("alb"), error_msg=request.args.get("error"))
        csrf_token=generate_csrf()
    except Exception as e:
        log_exception(e, context="アルバイト登録フォーム表示")
        return "Internal Server Error", 500

@alb_bp.route("/submit", methods=["POST"])
def submit():
    try:
        settings = load_settings()
        sheet = get_sheet("アルバイト登録シート")

        name = request.form.get("name", "")
        birthday4 = request.form.get("birthday4", "")
        experience_str = ", ".join(request.form.getlist("experience[]"))
        handslevel_str = ", ".join(request.form.getlist("handslevel[]"))
        area = request.form.get("area", "")
        available = request.form.get("available", "")
        reachtime = request.form.get("reachtime", "")
        user_id = request.form.get("user_id", "")
        custom_values = [request.form.get(field.get("name", ""), "") for field in settings.get("custom_fields", [])]

        birthday_full = f"20000302" if birthday4 == "0302" else f"2000{birthday4}" if len(birthday4) == 4 else ""
        register_user_info(name, birthday_full, app_liff_id=user_id)

        row = [name, birthday4, experience_str, handslevel_str, area, available, reachtime] + custom_values + [user_id]
        sheet.append_row(row)

        return "登録が完了しました！"
    except Exception as e:
        log_exception(e, context="アルバイト登録送信")
        return "Internal Server Error", 500

@alb_bp.route("/check", methods=["GET"])
def check_registration():
    try:
        user_id = request.args.get("user_id", "")
        sheet = get_sheet("アルバイト登録シート")
        registered_ids = [row[-1] for row in sheet.get_all_values()[1:]]
        return {"registered": user_id in registered_ids}
    except Exception as e:
        log_exception(e, context="登録確認")
        return {"error": "Internal error"}, 500
