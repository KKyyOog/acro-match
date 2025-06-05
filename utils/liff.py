# utils/liff.py

import os
from dotenv import load_dotenv

load_dotenv()  # .env を読み込む

def get_liff_id(page_type: str) -> str:
    """
    LIFFページ種別（例: 'classroom', 'alb', 'recruit'）に対応するLIFF IDを返す。
    環境変数が設定されていない場合は警告を出す。
    """
    key = f"LIFF_ID_{page_type.lower()}"
    value = os.getenv(key)
    if not value:
        print(f"⚠️ 環境変数 {key} が設定されていません。LIFF IDが取得できません。")
    return value or ""
