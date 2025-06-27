# utils/user.py
from utils.sheets import (
    append_row_if_new_user,
    update_liff_id_by_name_and_birthday4
)
from utils.logging_util import log_exception
from datetime import datetime
import re

def register_user_info(name: str, birthday: str, chat_liff_id: str = "", app_liff_id: str = ""):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        m = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", birthday)
        if m:
            birthday = f"{m.group(1)}{int(m.group(2)):02}{int(m.group(3)):02}"

        digits = ''.join(filter(str.isdigit, birthday))
        if len(digits) != 8:
            raise ValueError("誕生日は8桁の数値 (YYYYMMDD) である必要があります")

        if name and digits and app_liff_id:
            if update_liff_id_by_name_and_birthday4(name, digits[-4:], app_liff_id):
                return

        # それ以外は新規追加 or 情報補完
        append_row_if_new_user(name, birthday, chat_liff_id=chat_liff_id, app_liff_id=app_liff_id, timestamp=timestamp)

    except Exception as e:
        log_exception(e, context="register_user_info 処理")
