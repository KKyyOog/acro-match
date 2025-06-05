import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.logging_util import log_exception

SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Render用: GOOGLE_CREDENTIALS にJSONを直接環境変数として渡す
cred_json = os.getenv("GOOGLE_CREDENTIALS")
if not cred_json:
    raise ValueError("GOOGLE_CREDENTIALS not set")

try:
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(cred_json), SCOPES)
    gc = gspread.authorize(credentials)
except Exception as e:
    log_exception(e, context="Google認証")
    raise

def get_sheet(sheet_name):
    try:
        spreadsheet = gc.open_by_key(os.getenv("SPREADSHEET_ID"))
        return spreadsheet.worksheet(sheet_name)
    except Exception as e:
        log_exception(e, context=f"シート取得失敗: {sheet_name}")
        raise

def add_user_id_mapping_if_new(webhook_id: str, name: str):
    try:
        sheet = get_sheet("ユーザー対応表")
        ids = [row[0] for row in sheet.get_all_values()[1:]]
        if webhook_id not in ids:
            sheet.append_row([webhook_id, name])
    except Exception as e:
        log_exception(e, context="ユーザー追加失敗")

def update_birthday_if_exists(webhook_id: str, birthday: str) -> bool:
    try:
        sheet = get_sheet("ユーザー対応表")
        records = sheet.get_all_values()
        for idx, row in enumerate(records):
            if row and row[0] == webhook_id:
                sheet.update_cell(idx + 1, 3, birthday)
                return True
        return False
    except Exception as e:
        log_exception(e, context="誕生日更新失敗")
        return False

def update_liff_id_in_user_map(name: str, birthday4: str, liff_id: str) -> bool:
    try:
        sheet = get_sheet("ユーザー対応表")
        records = sheet.get_all_values()
        for idx, row in enumerate(records):
            if len(row) >= 3 and row[1] == name and row[2][-4:] == birthday4:
                if len(row) < 4:
                    row += [""] * (4 - len(row))
                sheet.update_cell(idx + 1, 4, liff_id)
                return True
        return False
    except Exception as e:
        log_exception(e, context="LIFF ID 更新失敗")
        return False

def update_sheet_headers_for_alb(sheet, settings):
    headers = [
        "名前", "生年月日(下4桁)", "経験", "補助レベル", "地域", "出勤可能日", "到着時間"
    ]
    for field in settings.get("custom_fields", []):
        headers.append(field.get("label", ""))
    headers.append("LINE ID")
    sheet.resize(rows=1)
    sheet.insert_row(headers, index=1)

def update_sheet_headers_for_classroom(sheet, settings):
    headers = [
        "教室名", "場所", "日時", "希望する経験", "補助レベル", "備考"
    ]
    for field in settings.get("custom_fields_classroom", []):
        headers.append(field.get("label", ""))
    headers.append("LINE ID")
    sheet.resize(rows=1)
    sheet.insert_row(headers, index=1)

def get_webhook_id_from_liff_id(liff_id: str) -> str:
    """
    ユーザー対応表から LIFF ID に対応する Webhook ID を探す
    """
    try:
        sheet = get_sheet("ユーザー対応表")
        for row in sheet.get_all_values():
            if len(row) >= 4 and row[3] == liff_id:
                return row[0]  # Webhook ID
    except Exception as e:
        log_exception(e, context="LIFF ID から Webhook ID 取得")
    return ""
