from flask import Flask
from blueprints.alb import alb_bp
from blueprints.classroom import classroom_bp
from blueprints.admin import admin_bp

app = Flask(__name__)

# Blueprint登録
app.register_blueprint(alb_bp)
app.register_blueprint(classroom_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)
