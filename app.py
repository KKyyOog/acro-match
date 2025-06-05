from flask import Flask, render_template, request, redirect, url_for, send_file, Response
from blueprints.alb import alb_bp
from blueprints.classroom import classroom_bp
from blueprints.callback import callback_bp
from blueprints.link import link_bp
from blueprints.admin import admin_bp
from dotenv import load_dotenv
import os
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret-key")

csrf = CSRFProtect()
csrf.init_app(app)
csrf.exempt(callback_bp)

load_dotenv()

# Blueprintの登録
app.register_blueprint(alb_bp)
app.register_blueprint(classroom_bp)
app.register_blueprint(callback_bp)
app.register_blueprint(link_bp)
app.register_blueprint(admin_bp)

@app.route("/")
def index():
    return Response("\U0001F4D8 Flask アプリ稼働中：/alb, /classroom, /callback, /link などのルートを確認してください。", content_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    app.run(debug=True)
