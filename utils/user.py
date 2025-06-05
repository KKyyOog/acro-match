# utils/user.py

from utils.sheets import (
    add_user_id_mapping_if_new,
    update_birthday_if_exists,
    update_liff_id_in_user_map
)

def register_user_info(name: str, birthday: str, liff_id: str):
    """
    ユーザー情報を一括登録：
    - Webhook ID (LIFF ID) と名前のマッピングを登録
    - 生年月日（任意）を登録
    - LIFF ID と名前＋生年月日下4桁をマッピング
    """
    add_user_id_mapping_if_new(webhook_id=liff_id, name=name)

    # 生年月日が指定されている場合のみ登録処理を行う
    if birthday:
        update_birthday_if_exists(liff_id, birthday)
        digits = ''.join(filter(str.isdigit, birthday))
        if len(digits) >= 4:
            last4 = digits[-4:]
            update_liff_id_in_user_map(name, last4, liff_id)
