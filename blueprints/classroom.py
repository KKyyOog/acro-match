# blueprints/classroom.py
from flask import Blueprint, request, render_template, jsonify, redirect, url_for
from utils.settings import load_settings
from utils.liff import get_liff_id
from utils.notify import send_line_message
from utils.logging_util import log_exception
from flask_wtf.csrf import generate_csrf
from utils.sheets import get_sheet, get_chat_liff_id_by_app_liff_id, highlight_classroom_row

classroom_bp = Blueprint("classroom", __name__, url_prefix="/classroom")

@classroom_bp.route("/form")
def show_form():
    return render_template(
        "form_classroom.html",
        settings=load_settings(),
        liff_id=get_liff_id("classroom"),
        csrf_token=generate_csrf()  # ← これを追加
    )
@classroom_bp.route("/submit", methods=["POST"])
def submit():
    try:
        settings = load_settings()
        sheet = get_sheet("教室登録シート")
        
        name = request.form.get("name")
        location = request.form.get("location")
        date = request.form.get("date")
        experience_list = request.form.getlist("experience[]")
        handslevel_list = request.form.getlist("handslevel[]")
        notes = request.form.get("notes", "")
        user_id = request.form.get("user_id", "")

        alb_sheet = get_sheet("アルバイト登録シート")
        registered_albs = [row[-1] for row in alb_sheet.get_all_values()[1:]]
        if user_id not in registered_albs:
            return redirect(url_for("alb.show_register_form", error="need_alb"))

        row = [
            name,
            location,
            date,
            ", ".join(experience_list),
            ", ".join(handslevel_list),
            notes,
        ]

        for field in settings.get("custom_fields_classroom", []):
            row.append(request.form.get(field.get("name", ""), ""))

        row.append(user_id)
        sheet.append_row(row)

        return "教室登録が完了しました！募集一覧に掲載されているかご確認ください。"
    except Exception as e:
        log_exception(e, context="教室登録送信")
        return "Internal Server Error", 500

@classroom_bp.route("/recruit", methods=["GET"])
def view_recruitment():
    try:
        settings = load_settings()
        liff_id = get_liff_id("recruit")
        sheet = get_sheet("教室登録シート")
        headers = sheet.row_values(1)
        rows = sheet.get_all_values()[1:]
        indexed_rows = [(i + 2, row) for i, row in enumerate(rows)]
        return render_template("view_classrooms.html", headers=headers, rows=indexed_rows, settings=settings, liff_id=liff_id)
    except Exception as e:
        log_exception(e, context="教室一覧表示")
        return "Internal Server Error", 500
 
@classroom_bp.route("/interest", methods=["POST"])
def handle_interest():
    try:
        data = request.get_json(force=True)
        print("📩 受信データ:", data)

        # Validate required fields
        if not data:
            print("❌ データが空です")
            return "Bad Request: Missing required data", 400
        if "row_index" not in data:
            print("❌ 'row_index' が不足しています")
            return "Bad Request: Missing 'row_index'", 400
        if "user_id" not in data:
            print("❌ 'user_id' が不足しています")
            return "Bad Request: Missing 'user_id'", 400

        row_index_raw = data.get("row_index")
        try:
            ow_index = int(row_index_raw)
        except ValueError:
            print("❌ 'row_index' の形式が不正です:", row_index_raw)
            return "Bad Request: Invalid 'row_index'", 400
        
        user_id = data.get("user_id")
        if not isinstance(user_id, str) or not user_id.startswith("U"):
            print("❌ 'user_id' の形式が不正です:", user_id)
            return "Bad Request: Invalid 'user_id'", 400
        
        print("🔎 row_index:", row_index_raw)
        print("🔎 user_id:", user_id)

        # Process the interest (e.g., send a notification)
        # Add your logic here...

        return "Interest recorded successfully", 200
    except Exception as e:
        log_exception(e, context="興味あり処理")
        return "Internal Server Error", 500