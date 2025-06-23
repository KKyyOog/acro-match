from flask import Flask
import threading
import time
import sys
import os

# モジュール検索パスに親ディレクトリを追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# PingService をインポート
from services.ping_service import PingService

app = Flask(__name__)

def monitor_server(url, interval=300):
    """
    サーバーの監視を行う関数。
    指定された URL に対して定期的に HTTP リクエストを送信し、結果をログに記録します。
    """
    ping_service = PingService()
    while True:
        result = ping_service.check_http(url)
        print(result)  # ログはすでに ping_service 内で記録される
        time.sleep(interval)

@app.route("/")
def health_check():
    """
    ヘルスチェック用のエンドポイント。
    """
    return "Monitor is running", 200

if __name__ == "__main__":
    # 監視スレッドを開始
    monitor_thread = threading.Thread(
        target=monitor_server,
        args=("https://acro-match.onrender.com", 300),  # 5分間隔で監視
        daemon=True
    )
    monitor_thread.start()

    # Flask サーバーを起動
    app.run(host="0.0.0.0", port=5000)