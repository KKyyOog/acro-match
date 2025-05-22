from flask import Flask
from flask_wtf.csrf import CSRFProtect
from blueprints.alb import alb_bp
from blueprints.classroom import classroom_bp
from blueprints.admin import admin_bp
from blueprints.callback import callback_bp  # ← 追加
import os
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

csrf = CSRFProtect(app)

# Blueprint登録
app.register_blueprint(alb_bp)
app.register_blueprint(classroom_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(callback_bp)  # ← 追加

if __name__ == "__main__":
    app.run(debug=True)
