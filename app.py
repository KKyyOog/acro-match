from flask import Flask, request, render_template, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import requests
import os
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
import logging
logging.basicConfig(level=logging.INFO)


app = Flask(__name__)

# ------------------------ 設定ファイル管理 ------------------------

def load_settings():
    """Load settings from a JSON file with default fallback."""
    default_settings = {
        "title": "アルバイト登録",
        "button_color": "#00b900",
        "form_label_name": "お名前",
        "form_label_area": "希望エリア",
        "form_label_available": "出勤可能日",
        "custom_fields": [],
        "classroom_title": "教室登録フォーム",
        "form_label_classroom_name": "教室名",
        "form_label_classroom_location": "場所",
        "form_label_classroom_date": "募集日時",
        "form_label_classroom_experience": "希望する経験"
    }
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            saved = json.load(f)
        return {**default_settings, **saved}
    except Exception as e:
        print(f"⚠️ load_settings error: {e}")
        return default_settings

def save_settings(data):
    """Save settings to a JSON file."""
    try:
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ save_settings error: {e}")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Admin page for updating settings."""
    if request.method == 'POST':
        new_settings = {
            "title": request.form.get("title"),
            "button_color": request.form.get("button_color"),
            "form_label_name": request.form.get("form_label_name"),
            "form_label_area": request.form.get("form_label_area"),
            "form_label_available": request.form.get("form_label_available"),
            "classroom_title": request.form.get("classroom_title"),
            "form_label_classroom_name": request.form.get("form_label_classroom_name"),
            "form_label_classroom_location": request.form.get("form_label_classroom_location"),
            "form_label_classroom_date": request.form.get("form_label_classroom_date"),
            "form_label_classroom_experience": request.form.get("form_label_classroom_experience"),
            "custom_fields": []
        }
        custom_count = int(request.form.get("custom_count", 0))
        for i in range(1, custom_count + 1):
            label = request.form.get(f"custom_label_{i}")
            name = request.form.get(f"custom_name_{i}")
            if label and name:
                new_settings["custom_fields"].append({"label": label, "name": name})

        save_settings(new_settings)
        return redirect('/admin')

    current_settings = load_settings()
    return render_template('admin.html', settings=current_settings)

# ------------------------ Google Sheets ------------------------

def get_sheet(sheet_name):
    """Authenticate and return a Google Sheet."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def ensure_headers_exist(sheet, base_headers, custom_fields):
    """Ensure the sheet has the correct headers."""
    current_headers = sheet.row_values(1)
    expected_headers = base_headers + [field.get("label", "") for field in custom_fields]

    if current_headers != expected_headers:
        sheet.delete_row(1)  # Remove old headers
        sheet.insert_row(expected_headers, 1)  # Insert new headers

def find_matching_alb(sheet, area, experience_required, datetime_str):
    all_rows = sheet.get_all_records()
    matched = []
    for row in all_rows:
        area_match = area in row.get("area", "")
        date_match = datetime_str[:10] in row.get("available", "")
        gym_match = experience_required == "体操経験者" and row.get("gym") == "あり"
        cheer_match = experience_required == "チアリーディング可" and row.get("cheer") == "あり"
        fallback_match = experience_required == "補助可能"

        # いずれか1つでも一致すればマッチとみなす
        if area_match or date_match or gym_match or cheer_match or fallback_match:
            matched.append(row.get("user_id"))
    return matched


# ------------------------ LINE通知 ------------------------

load_dotenv()
LINE_ACCESS_TOKEN = os.environ.get("LINE_ACCESS_TOKEN")

print(f"LINE_ACCESS_TOKEN: {LINE_ACCESS_TOKEN}")

def line_notify(to, message):
    """Send a LINE notification."""
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    body = {
        "to": to,
        "messages": [{"type": "text", "text": message}]
    }
    try:
        response = requests.post(url, headers=headers, json=body)
        print(f"📤 LINE送信先: {to}")
        print(f"📩 メッセージ: {message}")
        print(f"✅ 通知結果: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ LINE通知エラー: {e}")


@app.route('/notify_school', methods=['POST'])
def notify_school():
    school_user_id = request.form.get("school_user_id")
    school_name = request.form.get("school_name")

    if school_user_id:
        message = "案件に対して興味を示しているアルバイトがいます！ラインを交換しますか？"
        line_notify(school_user_id, message)
        return "通知を送信しました。戻るボタンで一覧に戻ってください。"
    else:
        return "エラー：通知先が不明です", 400



# ------------------------ 教室側 ------------------------

@app.route('/')
def index():
    """Render the classroom registration form."""
    settings = load_settings()
    return render_template('form_classroom.html', settings=settings)

@app.route('/submit', methods=['POST'])
def submit():
    """Handle classroom registration form submission."""
    name = request.form.get('name')
    location = request.form.get('location')
    datetime_str = request.form.get('date')
    experience = request.form.get('experience')
    user_id = request.form.get('user_id')

    try:
        sheet = get_sheet("教室登録シート")
        sheet.append_row([name, location, datetime_str, experience, user_id])
        return "教室登録と通知が完了しました！LINEに戻ってください。"
    except Exception as e:
        print(f"教室登録エラー: {e}")
        return "Internal Server Error", 500

# ------------------------ アルバイト側 ------------------------

@app.route('/register_alb')
def register_alb():
    """Render the part-time job registration form."""
    settings = load_settings()
    return render_template('form_alb.html', settings=settings)

@app.route('/submit_alb', methods=['POST'])
def submit_alb():
    """Handle part-time job registration form submission."""
    try:
        settings = load_settings()
        name = request.form.get('name')
        gym = request.form.get('gym')
        cheer = request.form.get('cheer')
        area = request.form.get('area')
        available = request.form.get('available')
        user_id = request.form.get('user_id')

        custom_values = [
            request.form.get(field.get("name", ""), "")
            for field in settings.get("custom_fields", [])
        ]

        sheet = get_sheet("アルバイト登録シート")
        row = [name, gym, cheer, area, available, user_id] + custom_values
        sheet.append_row(row)

        # Notify users
        matched_users = find_matching_alb(sheet, area, "補助可能", available)
        for matched_user_id in matched_users:
            line_notify(matched_user_id, f"{area}でアルバイト募集があります！応募はこちら ▶ https://...")

        if user_id:
            line_notify(user_id, f"{name}さん、アルバイト登録ありがとうございます！")
        else:
            print("user_idがNoneです。LINE通知はスキップされました。")

        return "登録が完了しました！"
    except Exception as e:
        print(f"submit_alb エラー: {e}")
        return "Internal Server Error", 500
    

@app.route('/recruit')
def view_classrooms():
    settings = load_settings()
    sheet = get_sheet("教室登録シート")
    headers = sheet.row_values(1)
    rows = sheet.get_all_values()[1:]  # データ行のみ
    indexed_rows = [(i + 2, row) for i, row in enumerate(rows)]  # 行番号とセット
    return render_template('view_classrooms.html', headers=headers, rows=indexed_rows, settings=settings)

@app.route("/interest", methods=["POST"])
def notify_interest_to_classroom_owner():
    try:
        row_index = int(request.form.get("row_index"))
        sheet = get_sheet("教室登録シート")
        user_id = sheet.cell(row_index, 5).value  # 5列目 = user_id列

        if user_id:
            school_name = sheet.cell(row_index, 1).value
            message = f"あなたが登録した教室「{school_name}」に興味を持った人がいます！"
            line_notify(user_id, message)
            return "通知を送信しました。戻るボタンで一覧に戻ってください。"
        else:
            return "通知先のuser_idが見つかりません。", 400
    except Exception as e:
        print(f"/interest エラー: {e}")
        return "Internal Server Error", 500


if __name__ == "__main__":
    test_user_id = "Uxxxxxxxxxxxxxxxxxx"  # あなたのLINE user_id に置き換える
    line_notify(test_user_id, "テスト通知：LINE通知確認用メッセージです")
    app.run(debug=True)


