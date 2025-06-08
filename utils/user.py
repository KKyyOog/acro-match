# utils/user.py
from utils.sheets import (
    append_row_if_new_user,
    update_app_liff_id_by_name_birthday
)
from utils.logging_util import log_exception
from datetime import datetime

def register_user_info(name: str, birthday: str, chat_liff_id: str = "", app_liff_id: str = ""):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 基本登録
        append_row_if_new_user(name, birthday, chat_liff_id=chat_liff_id, app_liff_id=app_liff_id, timestamp=timestamp)

        # アプリ側の LIFF ID がある場合は更新
        if app_liff_id and name and birthday:
            update_app_liff_id_by_name_birthday(name, birthday, app_liff_id)

    except Exception as e:
        log_exception(e, context="register_user_info 処理")
