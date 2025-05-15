from flask import Flask, request, render_template, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
import logging
logging.basicConfig(level=logging.INFO)


app = Flask(__name__)

# ------------------------ 設定ファイル管理 ------------------------

def load_settings():
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
    try:
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️ save_settings error: {e}")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
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
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def ensure_headers_exist(sheet, base_headers, custom_fields):
    current_headers = sheet.row_values(1)
    expected_headers = base_headers + [field.get("label", "") for field in custom_fields]

    if current_headers != expected_headers:
        sheet.delete_row(1)
        sheet.insert_row(expected_headers, 1)

def find_matching_alb(sheet, area, experience_required, datetime_str):
    all_rows = sheet.get_all_records()
    matched = []
    for row in all_rows:
        area_match = area in row.get("area", "")
        date_match = datetime_str[:10] in row.get("available", "")
        gym_match = experience_required == "体操経験者" and row.get("gym") == "あり"
        cheer_match = experience_required == "チアリーディング可" and row.get("cheer") == "あり"
        fallback_match = experience_required == "補助可能"

        if area_match or date_match or gym_match or cheer_match or fallback_match:
            matched.append(row.get("user_id"))
    return matched

# ------------------------ 教室側 ------------------------

@app.route('/')
def index():
    settings = load_settings()
    return render_template('form_classroom.html', settings=settings)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    location = request.form.get('location')
    datetime_str = request.form.get('date')
    experience = request.form.get('experience')
    user_id = request.form.get('user_id')

    try:
        sheet = get_sheet("教室登録シート")
        sheet.append_row([name, location, datetime_str, experience, user_id])
        return "教室登録が完了しました！LINEに戻ってください。"
    except Exception as e:
        print(f"教室登録エラー: {e}")
        return "Internal Server Error", 500

# ------------------------ アルバイト側 ------------------------

@app.route('/register_alb')
def register_alb():
    settings = load_settings()
    return render_template('form_alb.html', settings=settings)

@app.route('/submit_alb', methods=['POST'])
def submit_alb():
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

        return "登録が完了しました！"
    except Exception as e:
        print(f"submit_alb エラー: {e}")
        return "Internal Server Error", 500

# ------------------------ 教室一覧＆興味通知（LINE通知なし） ------------------------

@app.route('/recruit')
def view_classrooms():
    settings = load_settings()
    sheet = get_sheet("教室登録シート")
    headers = sheet.row_values(1)
    rows = sheet.get_all_values()[1:]
    indexed_rows = [(i + 2, row) for i, row in enumerate(rows)]
    return render_template('view_classrooms.html', headers=headers, rows=indexed_rows, settings=settings)

@app.route("/interest", methods=["POST"])
def notify_interest_placeholder():
    row_index = request.form.get("row_index")
    print(f"興味ありが押されました（行番号: {row_index}）。通知は省略中。")
    return "通知処理は現在無効化されています。"

if __name__ == "__main__":
    app.run(debug=True)