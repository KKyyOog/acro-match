# app.py

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from blueprints.alb import alb_bp
from blueprints.classroom import classroom_bp
from blueprints.callback import callback_bp
from blueprints.link import link_bp
from blueprints.admin import admin_bp
from dotenv import load_dotenv
import os
print("GOOGLE_CREDENTIALS:", os.getenv("GOOGLE_CREDENTIALS")[:50])
load_dotenv()  # 環境変数の読み込み（ローカル実行時用）

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default-dev-key")  # Renderなどの本番環境ではenvから取得

csrf = CSRFProtect(app)

# 各機能モジュールをBlueprintとして登録
app.register_blueprint(alb_bp)
app.register_blueprint(classroom_bp)
app.register_blueprint(callback_bp)
app.register_blueprint(link_bp)
app.register_blueprint(admin_bp)

@app.route("/")
def index():
    return "\ud83d\udcd8 Flask アプリ稼働中：/alb, /classroom, /callback, /link などのルートを確認してください。"

if __name__ == "__main__":
    app.run(debug=True)
