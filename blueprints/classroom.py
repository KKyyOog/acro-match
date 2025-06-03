from flask import Blueprint, request, render_template
from utils.sheets import get_sheet, load_settings, find_matching_alb
from utils.notify import send_line_message
from utils.liff import get_liff_id
from flask import jsonify, redirect, url_for

classroom_bp = Blueprint('classroom', __name__)

# 🔧 教室用シートのヘッダーを動的に更新する関数
def update_sheet_headers_for_classroom(sheet, settings):
    headers = [
        settings.get("form_label_classroom_name", "教室名"),
        settings.get("form_label_classroom_location", "場所"),
        settings.get("form_label_classroom_date", "募集日時"),
        settings.get("form_label_classroom_experience", "希望する経験（複数選択可"),
        settings.get("form_label_classroom_handslevel", "補助レベル（複数選択可）"),
        settings.get("form_label_classroom_notes", "その他ご要望・自由記述"),
    ]
    for field in settings.get("custom_fields_classroom", []):
        headers.append(field.get("label", ""))
    headers.append("user_id")

    sheet.delete_rows(1)
    sheet.insert_row(headers, index=1)

@classroom_bp.route("/")
def index():
    settings = load_settings()
    liff_id = get_liff_id("classroom")
    return render_template("form_classroom.html", settings=settings, liff_id=liff_id)

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
        experience_str = ", ".join(experience_list)

        handslevel_list = request.form.getlist("handslevel")
        handslevel_str = ", ".join(handslevel_list)

        notes = request.form.get("notes", "")
        
        # user_idの取得とアルバイト登録済みかどうか確認
        user_id = request.form.get("user_id", "")
        alb_sheet = get_sheet("アルバイト登録シート")
        registered_albs = [row[-1] for row in alb_sheet.get_all_values()[1:]]

        if user_id not in registered_albs:
            return redirect(url_for('alb.register_alb', error="need_alb"))


        # 📋 書き込む行の初期データ
        row = [
            name,
            location,
            date,
            experience_str,
            handslevel_str,
            notes
        ]

        # 🧩 カスタム項目を追加
        for field in settings.get("custom_fields_classroom", []):
            row.append(request.form.get(field.get("name", ""), ""))

        # 🆔 LINE user_id を最後に追加
        row.append(request.form.get("user_id", ""))

        # 📤 Google Sheets に追記
        sheet.append_row(row)

        return "教室登録が完了しました！募集一覧に掲載されているかご確認ください。"
    except Exception as e:
        print(f"教室登録エラー: {e}")
        return "Internal Server Error", 500


@classroom_bp.route("/recruit")
def view_classrooms():
    settings = load_settings()
    liff_id = get_liff_id("recruit")
    sheet = get_sheet("教室登録シート")
    headers = sheet.row_values(1)
    rows = sheet.get_all_values()[1:]
    indexed_rows = [(i + 2, row) for i, row in enumerate(rows)]
    return render_template("view_classrooms.html", headers=headers, rows=indexed_rows, settings=settings, liff_id=liff_id)

@classroom_bp.route("/interest", methods=["POST"])
def notify_interest():
    try:
        data = request.get_json()
        row_index = int(data.get("row_index"))
        user_id = data.get("user_id")  # 押した人（アルバイト）のuser_id

        sheet = get_sheet("教室登録シート")
        row = sheet.row_values(row_index)

        name = row[0]
        location = row[1]
        datetime_str = row[2]
        target_line_id = row[-1]  # ✅ 行の最後の列が教室側user_idであると仮定

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
        print("通知処理エラー:", e)
        return "Internal Server Error", 500

@classroom_bp.route("/check_alb_registered")
def check_alb_registered():
    user_id = request.args.get("user_id", "")
    alb_sheet = get_sheet("アルバイト登録シート")
    registered_albs = [row[-1] for row in alb_sheet.get_all_values()[1:]]
    return jsonify({"registered": user_id in registered_albs})