import unittest
import sys
import os
import logging

# srcディレクトリをモジュール検索パスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.ping_service import PingService

# テスト用ロガーを有効化
test_logger = logging.getLogger("test_logger")
if not test_logger.hasHandlers():
    test_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler("debug.log", mode="w")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    test_logger.addHandler(file_handler)

# ログのテスト
test_logger.debug("Test logger initialized")

# 定数
VALID_HOST = "google.com"
INVALID_HOST = "invalid.host"

class TestPingService(unittest.TestCase):

    def setUp(self):
        self.ping_service = PingService()

    def test_ping_success(self):
        response = self.ping_service.ping(VALID_HOST)
        test_logger.debug(f"Ping success response: {response}")
        print(f"Debug: Ping success response -> {response}")
        self.assertIn("Reply from", response)

    def test_ping_failure(self):
        response = self.ping_service.ping(INVALID_HOST)
        test_logger.debug(f"Ping failure response: {response}")
        print(f"Debug: Ping failure response -> {response}")
        self.assertIn("Ping failed for host", response)

    def test_ping_timeout(self):
        response = self.ping_service.ping("10.255.255.1")  # 存在しないIPアドレス
        test_logger.debug(f"Ping timeout response: {response}")
        print(f"Debug: Ping timeout response -> {response}")
        self.assertIn("Ping timeout for host", response)

    def test_invalid_host(self):
        response = self.ping_service.ping("")
        test_logger.debug(f"Invalid host response: {response}")
        print(f"Debug: Invalid host response -> {response}")
        self.assertIn("Ping exception for host", response)

if __name__ == '__main__':
    unittest.main()