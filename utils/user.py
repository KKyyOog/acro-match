# utils/user.py
from utils.sheets import (
    add_user_id_mapping_if_new,
    update_birthday_if_exists,
    update_liff_id_in_user_map
)
from utils.logging_util import log_exception

def register_user_info(name: str, birthday: str, liff_id: str):
    """
    ユーザー情報を一括登録：
    - Webhook ID (LIFF ID) と名前のマッピング
    - 生年月日の更新（存在する場合）
    - LIFF ID による生年月日下4桁とのリンク
    """
    try:
        add_user_id_mapping_if_new(webhook_id=liff_id, name=name)

        if birthday:
            update_birthday_if_exists(liff_id, birthday)
            digits = ''.join(filter(str.isdigit, birthday))
            if len(digits) >= 4:
                last4 = digits[-4:]
                update_liff_id_in_user_map(name, last4, liff_id)

    except Exception as e:
        log_exception(e, context="register_user_info 処理")
