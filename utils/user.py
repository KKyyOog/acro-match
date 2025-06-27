# utils/user.py
from utils.sheets import (
    append_row_if_new_user,
    update_liff_id_by_name_and_birthday4
)
from utils.logging_util import log_exception
from datetime import datetime

def register_user_info(name: str, birthday: str, chat_liff_id: str = "", app_liff_id: str = ""):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        digits = ''.join(filter(str.isdigit, birthday))
        if len(digits) != 8:
            raise ValueError("誕生日は8桁の数値 (YYYYMMDD) である必要があります")

        # アプリ側 LIFF ID のみ更新する場合（名前 + 誕生日下4桁）
        if name and birthday and app_liff_id:
            digits = ''.join(filter(str.isdigit, birthday))
            if len(digits) >= 4 and update_liff_id_by_name_and_birthday4(name, digits[-4:], app_liff_id):
                return

        # それ以外は新規追加 or 情報補完
        append_row_if_new_user(name, birthday, chat_liff_id=chat_liff_id, app_liff_id=app_liff_id, timestamp=timestamp)

    except Exception as e:
        log_exception(e, context="register_user_info 処理")
