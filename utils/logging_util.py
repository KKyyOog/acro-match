import logging
import traceback

# ロガーの設定
logger = logging.getLogger("acro_match")
logger.setLevel(logging.DEBUG)  # ログレベルを設定（DEBUG, INFO, WARNING, ERROR, CRITICAL）

# コンソールハンドラーを追加
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# ログのフォーマットを設定
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(formatter)

# ロガーにハンドラーを追加
logger.addHandler(console_handler)

def log_exception(e: Exception, context: str = ""):
    """エラーログを整形して出力するユーティリティ関数"""
    logger.error(f"❌ {context} エラー: {e}")
    logger.error(traceback.format_exc())

def log_info(message: str, context: str = ""):
    """情報ログを出力するユーティリティ関数"""
    logger.info(f"ℹ️ {context}: {message}")

def log_error(message: str, context: str = ""):
    """警告ログを出力するユーティリティ関数"""
    logger.warning(f"⚠️ {context}: {message}")