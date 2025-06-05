import os
import requests
from dotenv import load_dotenv
from utils.sheets import get_webhook_id_from_liff_id

load_dotenv()

LINE_API_URL = "https://api.line.me/v2/bot/message/push"
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

def send_line_message(user_id, message_text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message_text}]
    }
    print("送信ペイロード:", payload)
    response = requests.post(LINE_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print("⚠️ LINE通知エラー:", response.status_code, response.text)
        return False
    print("✅ 通知送信成功")
    return True


def notify_classroom_of_interest(liff_id, interested_user_name="誰かが"):
    webhook_id = get_webhook_id_from_liff_id(liff_id)
    if webhook_id:
        message = f"{interested_user_name} あなたの募集に興味を持っています！"
        return send_line_message(webhook_id, message)
    else:
        print("❌ 対応するWebhook IDが見つかりません")
        return False


# テスト用に直接実行される場合
#if __name__ == "__main__":
#    test_user_id = "U90ce70715f2e5f6eddfc0dab100afc17"
#    success = send_line_message(test_user_id, "テスト通知です")
#    print("✅ 通知送信成功:", success)
#    print("✅ 新規フォローユーザーID:", test_user_id)
