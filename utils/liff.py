# utils/liff.py
import os
from dotenv import load_dotenv

load_dotenv()  # .env を読み込む

def get_liff_id(page_type):
    key = f"LIFF_ID_{page_type.lower()}"
    return os.getenv(key)
