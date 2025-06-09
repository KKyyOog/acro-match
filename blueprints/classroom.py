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
        # 設定データとLIFF IDを取得
        settings = load_settings()
        liff_id = get_liff_id("recruit")

        # スプレッドシートからデータを取得
        sheet = get_sheet("教室登録シート")
        headers = sheet.row_values(1)  # ヘッダー行を取得
        rows = sheet.get_all_values()[1:]  # データ行を取得（ヘッダーを除く）

        # 各行にインデックスを付与
        indexed_rows = [(i + 1, row) for i, row in enumerate(rows)]

        # テンプレートに渡すコンテキストを準備
        context = {
            "headers": headers,  # ヘッダー
            "rows": indexed_rows,  # インデックス付きデータ行
            "settings": settings,  # 設定データ
            "liff_id": liff_id,  # LIFF ID
        }

        # テンプレートをレンダリング
        return render_template("view_classrooms.html", **context)

    except Exception as e:
        # エラーをログに記録し、500エラーを返す
        log_exception(e, context="教室一覧表示")
        return "Internal Server Error", 500
    
@classroom_bp.route("/interest", methods=["POST"])
def handle_interest():
    try:
        # クライアントから送信されたデータを取得
        data = request.get_json(force=True)
        if data is None:
            print("❌ JSON データが解析できませんでした")
            return "Bad Request: Invalid JSON", 400

        print("📩 サーバーが受信したデータ:", data)

        # row_index を取得
        row_index_raw = data.get("row_index")
        try:
            row_index = int(row_index_raw)
        except ValueError:
            print("❌ 'row_index' の形式が不正です:", row_index_raw)
            return "Bad Request: Invalid 'row_index'", 400

        print(f"🔔 興味ボタンが押されました！ row_index: {row_index}")

        return "Interest button clicked", 200
    except Exception as e:
        import traceback
        print("❌ エラーが発生しました:", traceback.format_exc())
        return "Internal Server Error", 500