# utils/user.py
from utils.sheets import append_row_if_new_user
from utils.sheets import (
     append_row_if_new_user,
     update_liff_id_by_name_birthday
 )
from utils.logging_util import log_exception

def register_user_info(name: str, birthday: str, liff_id: str = "", webhook_event_id: str = None):
    try:
        # Webhook ID がある場合（チャット登録）
        if webhook_event_id:
            append_row_if_new_user(name, birthday, "", webhook_id=webhook_event_id)

        # LIFF ID がある場合（アルバイト登録時など）
        if liff_id and name and birthday:
            update_liff_id_by_name_birthday(name, birthday, liff_id)

    except Exception as e:
        log_exception(e, context="register_user_info 処理")
