from flask import Blueprint, request, render_template
from utils.sheets import get_sheet, load_settings, find_matching_alb
from utils.notify import send_line_message
from utils.liff import get_liff_id

classroom_bp = Blueprint('classroom', __name__)

# 🔧 教室用シートのヘッダーを動的に更新する関数
def update_sheet_headers_for_classroom(sheet, settings):
    headers = [
        settings.get("form_label_classroom_name", "教室名"),
        settings.get("form_label_classroom_location", "場所"),
        settings.get("form_label_classroom_date", "募集日時"),
        settings.get("form_label_classroom_experience", "希望する経験")
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

        # ✅ ヘッダーを更新
        update_sheet_headers_for_classroom(sheet, settings)

        # 🔁 フォーム入力の取得
        experience_list = request.form.getlist("experience")
        experience_str = ", ".join(experience_list)

        row = [
            request.form.get("name"),
            request.form.get("location"),
            request.form.get("date"),
            experience_str,
        ]

        # 🔁 カスタム項目も取得
        for field in settings.get("custom_fields_classroom", []):
            row.append(request.form.get(field.get("name", ""), ""))

        row.append(request.form.get("user_id", ""))

        sheet.append_row(row)
        return "教室登録が完了しました！LINEに戻ってください。"
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
    row_index = int(request.form.get("row_index"))
    user_id = request.form.get("user_id")  # アルバイトのLINE user_id

    try:
        sheet = get_sheet("教室登録シート")
        row = sheet.row_values(row_index)

        name = row[0]
        location = row[1]
        datetime_str = row[2]

        target_line_id = "Uxxxxxxxxxxxxxxxxxxxxxxxxxxx"

        message = (
            f"📢 アルバイトから興味ありの通知がありました！\n"
            f"教室名：{name}\n"
            f"場所：{location}\n"
            f"日時：{datetime_str}\n"
            f"連絡先（user_id）：{user_id}"
        )

        send_line_message(target_line_id, message)
        return "通知を送信しました！"
    except Exception as e:
        print("通知処理エラー:", e)
        return "Internal Server Error", 500
