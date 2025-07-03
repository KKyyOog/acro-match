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
        liff_id = request.form.get("liff_id")  # ここでliff_idを取得
        user_id = liff_id  # liff_idをuser_idとして扱う
        classroom_name = request.form.get("classroom_name")
        location = request.form.get("location")
        date = request.form.get("date")
        experience = request.form.getlist("experience[]")
        handslevel = request.form.getlist("handslevel[]")
        details = request.form.get("details")

        # user_id, classroom_nameの必須チェック
        if not user_id or not classroom_name:
            log_error("必須フィールドが不足しています")
            return "Bad Request: Missing required fields", 400

        # スプレッドシートにデータを追加
        sheet = get_sheet("教室登録シート")
        row = [
            classroom_name,
            location,
            date,
            ",".join(experience),
            ",".join(handslevel),
            details,
            liff_id
        ]
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

        # ヘッダーからLIFF ID列を削除
        headers = headers[:-1]  # 最後の列（LIFF ID）を削除

        # 各行から「その他自由記述」を分離し、ポップアップ用に保持
        processed_rows = []
        for row in rows:
            popup_data = row[-2]  # その他自由記述（最後から2番目の列）
            row_data = row[:-2]  # 表に表示するデータ（その他自由記述とLIFF IDを除外）
            processed_rows.append((popup_data, row_data))

        # 各行にインデックスを付与
        indexed_rows = [(i + 1, popup_data, row_data) for i, (popup_data, row_data) in enumerate(processed_rows)]
        log_info(f"教室募集一覧を取得しました: {indexed_rows}")

        context = {
            "headers": headers[:-1],  # 表に表示するヘッダー（その他自由記述を除外）
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

        # スプレッドシートから該当する行を取得
        sheet = get_sheet("教室登録シート")
        rows = sheet.get_all_values()[1:]  # ヘッダーを除いたデータ行を取得

        if row_index < 1 | row_index > len(rows):
            log_error(f"row_index が範囲外です: {row_index}")
            return "Bad Request: 'row_index' out of range", 400

        selected_row = rows[row_index - 1]  # row_index は 1ベースなので -1 する
        classroom_name = selected_row[0]  # 教室名は行の最初の列にあると仮定
        app_liff_id = selected_row[-1]  # アプリ LIFF ID は行の最後の列にあると仮定

        log_info(f"選択された教室名: {classroom_name}")
        log_info(f"選択されたアプリ LIFF ID: {app_liff_id}")

        # ユーザー情報シートから該当する行を探す
        user_sheet = get_sheet("ユーザー情報")
        user_rows = user_sheet.get_all_values()[1:]  # ヘッダーを除いたデータ行を取得

        log_info(f"ユーザー情報シートのデータ: {user_rows}")

        matching_row = None
        for user_row in user_rows:
            log_info(f"チェック中の行: {user_row}")
            if user_row[3] == app_liff_id:  # アプリ LIFF ID が一致する行を探す
                matching_row = user_row
                break

        if matching_row:
            log_info(f"対応するユーザー情報行: {matching_row}")
            chat_liff_id = matching_row[2]  # 該当行のチャット LIFF ID を取得

            # 通知メッセージを送信
            message = f"教室名: {classroom_name} に興味があると通知されました！"
            try:
                send_line_message(chat_liff_id, message)  # LINE Notify API を使用してメッセージを送信
                log_info(f"通知メッセージを送信しました: {message}")
            except Exception as notify_error:
                log_exception(notify_error, context="通知メッセージ送信")
                return "Internal Server Error: Failed to send notification", 500

            return jsonify({"classroom_name": classroom_name, "matching_row": matching_row}), 200
        else:
            log_error(f"アプリ LIFF ID '{app_liff_id}' に対応する行が見つかりません。ユーザー情報シートを確認してください。")
            return "Bad Request: No matching row found", 400

    except Exception as e:
        log_exception(e, context="興味ありリクエスト処理")
        return "Internal Server Error", 500