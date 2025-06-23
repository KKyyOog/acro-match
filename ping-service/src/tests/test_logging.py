import logging

# ログ設定
logging.basicConfig(
    filename="monitor.log",  # ログファイル名
    level=logging.DEBUG,  # DEBUGレベル以上のログを記録
    format="%(asctime)s - %(levelname)s - %(message)s"  # ログのフォーマット
)

# ログのテスト
logging.debug("Test: Logging system initialized")
logging.info("Test: This is an INFO message")
logging.warning("Test: This is a WARNING message")
logging.error("Test: This is an ERROR message")
logging.critical("Test: This is a CRITICAL message")

# フラッシュを強制
logging.shutdown()