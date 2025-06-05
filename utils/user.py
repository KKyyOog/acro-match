# utils/user.py
from utils.sheets import append_row_if_new_user
from utils.sheets import (
     append_row_if_new_user,
     update_birthday_if_exists,
     update_liff_id_in_user_map
 )
from utils.logging_util import log_exception

def register_user_info(name: str, birthday: str, liff_id: str, webhook_event_id: str = None):
    try:
        append_row_if_new_user(name=name, webhook_id=webhook_event_id)

        if birthday:
            update_birthday_if_exists(liff_id, birthday)
            digits = ''.join(filter(str.isdigit, birthday))
            if len(digits) >= 4:
                last4 = digits[-4:]
                update_liff_id_in_user_map(name, last4, liff_id)
    except Exception as e:
        log_exception(e, context="register_user_info 処理")
