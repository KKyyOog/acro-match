# blueprints/classroom.py

from flask import Blueprint, request, render_template, jsonify, redirect, url_for
from utils.sheets import get_sheet, load_settings, update_sheet_headers_for_classroom
from utils.liff import get_liff_id
from utils.notify import send_line_message
from utils.logging_util import log_exception

classroom_bp = Blueprint("classroom", __name__, url_prefix="/classroom")

@classroom_bp.route("/form", methods=["GET"])
def show_form():
    try:
        settings = load_settings()
        liff_id = get_liff_id("classroom")
        return render_template("form_classroom.html", settings=settings, liff_id=liff_id)
    except Exception as e:
        log_exception(e, context="教室フォーム表示")
        return "Internal Server Error", 500

@classroom_bp.route("/submit", methods=["POST"])
def submit():
    try:
        settings = load_settings()
        sheet = get_sheet("教室登録シート")

        # ✅ ヘッダー更新
        update_sheet_headers_for_classroom(sheet, settings)

        # 🔁 フォーム入力の取得
        name = request.form.get("name")
        location = request.form.get("location")
        date = request.form.get("date")
        experience_list = request.form.getlist("experience")
        handslevel_list = request.form.getlist("handslevel")
        notes = request.form.get("notes", "")
        user_id = request.form.get("user_id", "")

        # 登録確認：アルバイト登録済かどうか
        alb_sheet = get_sheet("アルバイト登録シート")
        registered_albs = [row[-1] for row in alb_sheet.get_all_values()[1:]]
        if user_id not in registered_albs:
            return redirect(url_for("alb.show_register_form", error="need_alb"))

        # 📋 書き込む行の構築
        row = [
            name,
            location,
            date,
            ", ".join(experience_list),
            ", ".join(handslevel_list),
            notes,
        ]

        # カスタム項目を追加
        for field in settings.get("custom_fields_classroom", []):
            row.append(request.form.get(field.get("name", ""), ""))

        row.append(user_id)  # user_id を最後に

        # 📤 Google Sheets に追記
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
def notify_interest():
    try:
        data = request.get_json(force=True)

        if not data or "row_index" not in data or "user_id" not in data:
            return "row_index または user_id がありません", 400

        row_index = int(data["row_index"])
        user_id = data.get("user_id")

        sheet = get_sheet("教室登録シート")
        row = sheet.row_values(row_index)

        name = row[0]
        location = row[1]
        datetime_str = row[2]
        target_line_id = row[-1]

        message = (
            f"📢 アルバイトから興味ありの通知がありました！\n"
            f"教室名：{name}\n"
            f"場所：{location}\n"
            f"日時：{datetime_str}\n"
            f"連絡先：{user_id}"
        )

        send_line_message(target_line_id, message)
        return "通知を送信しました！"
    except Exception as e:
        log_exception(e, context="興味通知")
        return "Internal Server Error", 500
