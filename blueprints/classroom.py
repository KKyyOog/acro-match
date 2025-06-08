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
        user_app_liff_id = data.get("user_id")  # LIFF 経由で取得
        row_index = data.get("row_index", -1)
        print("🧩 row_index raw:", row_index)
        print("🧩 user_id:", user_app_liff_id)

        try:
            row_index = int(row_index)
        except (TypeError, ValueError):
            return {"error": "row_index が整数でない"}, 400
        
        if row_index < 0 or not user_app_liff_id:
            return {"error": "無効な入力"}, 400
        
        # ここで実際の処理（色変更など）を行う
        highlight_classroom_row(row_index)

        classroom_sheet = get_sheet("教室登録シート")
        classroom_rows = classroom_sheet.get_all_values()

        if row_index + 1 >= len(classroom_rows):
            return {"error": "行が存在しません"}, 404

        row = classroom_rows[row_index + 1]  # ヘッダーを除いた実行対象
        classroom_name = row[0] if len(row) > 0 else "（名称不明）"

        # ユーザー情報からチャット用LIFF IDを取得
        chat_liff_id = get_chat_liff_id_by_app_liff_id(user_app_liff_id)
        if not chat_liff_id:
            return {"error": "ユーザーが見つかりません"}, 404

        # 通知送信
        msg = f"あなたの教室「{classroom_name}」に興味を持っている人がいます！"
        success, err = send_line_message(chat_liff_id, msg)
        if not success:
            return {"error": err}, 500

        return {"message": "通知送信完了"}, 200

    except Exception as e:
        print("❌ 教室興味通知エラー:", e)
        return {"error": "サーバーエラー"}, 500
    
