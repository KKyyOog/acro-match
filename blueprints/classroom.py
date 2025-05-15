from flask import Blueprint, request, render_template
from utils.sheets import get_sheet, load_settings, find_matching_alb
from utils.notify import send_line_message

classroom_bp = Blueprint('classroom', __name__)

@classroom_bp.route("/")
def index():
    settings = load_settings()
    liff_id = get_liff_id("classroom")
    return render_template("form_classroom.html", settings=settings, liff_id=liff_id)

@classroom_bp.route("/submit", methods=["POST"])
def submit():
    try:
        sheet = get_sheet("教室登録シート")
        sheet.append_row([
            request.form.get("name"),
            request.form.get("location"),
            request.form.get("date"),
            request.form.get("experience"),
            request.form.get("user_id")
        ])
        return "教室登録が完了しました！LINEに戻ってください。"
    except Exception as e:
        print(f"教室登録エラー: {e}")
        return "Internal Server Error", 500

@classroom_bp.route("/recruit")
def view_classrooms():
    settings = load_settings()
    liff_id = get_liff_id("recruit")  # ←ここ！
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
        row = sheet.row_values(row_index)  # 該当行の教室データを取得

        name = row[0]
        location = row[1]
        datetime_str = row[2]

        # 📢 教室主のLINE IDを仮に固定（本番ではシートやDBから取得）
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