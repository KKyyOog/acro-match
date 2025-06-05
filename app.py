# app.py

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from blueprints.alb import alb_bp
from blueprints.classroom import classroom_bp
from blueprints.callback import callback_bp
from blueprints.link import link_bp
from blueprints.admin import admin_bp

app = Flask(__name__)
app.secret_key = "your-secret-key"  # CSRF用に必須

csrf = CSRFProtect(app)

# 各機能モジュールをBlueprintとして登録
app.register_blueprint(alb_bp)
app.register_blueprint(classroom_bp)
app.register_blueprint(callback_bp)
app.register_blueprint(link_bp)
app.register_blueprint(admin_bp)

# ルート確認用のトップページ（任意）
@app.route("/")
def index():
    return "📘 Flask アプリ稼働中：/alb, /classroom, /callback, /link などのルートを確認してください。"

# アプリ起動
if __name__ == "__main__":
    app.run(debug=True)
