# utils/logging_util.py
import traceback

def log_exception(e: Exception, context: str = ""):
    """エラーログを整形して出力するユーティリティ関数"""
    print(f"❌ {context} エラー: {e}")
    print(traceback.format_exc())