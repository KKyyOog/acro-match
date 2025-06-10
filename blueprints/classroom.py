# blueprints/classroom.py
from flask import Blueprint, request, render_template, jsonify, redirect, url_for
from utils.settings import load_settings
from utils.liff import get_liff_id
from utils.notify import send_line_message
from flask_wtf.csrf import generate_csrf
from utils.sheets import get_sheet, get_chat_liff_id_by_app_liff_id, highlight_classroom_row
from utils.logging_util import log_info, log_error, log_exception

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
        # フォームデータを取得
        user_id = request.form.get("user_id")
        classroom_name = request.form.get("classroom_name")
        details = request.form.get("details")

        if not user_id or not classroom_name:
            log_error("必須フィールドが不足しています")
            return "Bad Request: Missing required fields", 400

        # スプレッドシートにデータを追加
        sheet = get_sheet()
        row = [user_id, classroom_name, details]
        sheet.append_row(row)
        log_info(f"教室登録が完了しました: {row}")

        return "教室登録が完了しました！募集一覧に掲載されているかご確認ください。"

    except Exception as e:
        log_exception(e, context="教室登録送信")
        return "Internal Server Error", 500

@classroom_bp.route("/recruit", methods=["GET"])
def view_recruitment():
    try:
        # 設定データと LIFF ID を取得
        settings = load_settings()
        liff_id = get_liff_id("recruit")

        # スプレッドシートからデータを取得
        sheet = get_sheet("教室登録シート")
        headers = sheet.row_values(1)  # ヘッダー行を取得
        rows = sheet.get_all_values()[1:]  # データ行を取得（ヘッダーを除く）

        if not headers or not rows:
            log_error("スプレッドシートのデータが空です")
            return "No data available", 404

        # 各行にインデックスを付与
        indexed_rows = [(i + 1, row) for i, row in enumerate(rows)]
        log_info(f"教室募集一覧を取得しました: {indexed_rows}")

        # テンプレートに渡すコンテキストを準備
        context = {
            "headers": headers,
            "rows": indexed_rows,
            "settings": settings,
            "liff_id": liff_id,
        }

        return render_template("view_classrooms.html", **context)

    except Exception as e:
        log_exception(e, context="教室募集一覧表示")
        return "Internal Server Error", 500
    
@classroom_bp.route("/interest", methods=["POST"])
def handle_interest():
    try:
        # JSON データを取得
        data = request.get_json(force=True)
        if data is None:
            log_error("JSON データが解析できませんでした")
            return "Bad Request: Invalid JSON", 400

        log_info(f"サーバーが受信したデータ: {data}")

        # row_index の検証
        row_index_raw = data.get("row_index")
        try:
            row_index = int(row_index_raw)
        except ValueError:
            log_error(f"'row_index' の形式が不正です: {row_index_raw}")
            return "Bad Request: Invalid 'row_index'", 400

        log_info(f"興味ボタンが押されました！ row_index: {row_index}")
        return "Interest button clicked", 200

    except Exception as e:
        log_exception(e, context="興味ありリクエスト処理")
        return "Internal Server Error", 500