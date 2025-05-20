from flask import Blueprint, request, render_template, redirect
from utils.sheets import load_settings, save_settings
import json

def load_settings():
    with open("settings.json", "r", encoding="utf-8") as f:
        return json.load(f)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route("/", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        settings = {}

        # アルバイト用設定
        settings["form_title"] = request.form.get("form_title", "")
        settings["form_button_color"] = request.form.get("form_button_color", "")
        settings["form_label_name"] = request.form.get("form_label_name", "")
        settings["form_label_area"] = request.form.get("form_label_area", "")
        settings["form_label_available"] = request.form.get("form_label_available", "")

        form_count = int(request.form.get("custom_form_count", 0))
        form_fields = []
        for i in range(1, form_count + 1):
            label = request.form.get(f"custom_form_label_{i}")
            name = request.form.get(f"custom_form_name_{i}")
            if label and name:
                form_fields.append({"label": label, "name": name})
        settings["custom_fields_form"] = form_fields

        # 教室用設定
        settings["classroom_title"] = request.form.get("classroom_title", "")
        settings["form_label_classroom_name"] = request.form.get("form_label_classroom_name", "")
        settings["form_label_classroom_location"] = request.form.get("form_label_classroom_location", "")
        settings["form_label_classroom_date"] = request.form.get("form_label_classroom_date", "")
        settings["form_label_classroom_experience"] = request.form.get("form_label_classroom_experience", "")

        classroom_count = int(request.form.get("custom_classroom_count", 0))
        classroom_fields = []
        for i in range(1, classroom_count + 1):
            label = request.form.get(f"custom_classroom_label_{i}")
            name = request.form.get(f"custom_classroom_name_{i}")
            if label and name:
                classroom_fields.append({"label": label, "name": name})
        settings["custom_fields_classroom"] = classroom_fields

        # JSONに保存
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

        return redirect("/admin")

    # GET時は読み込んで表示
    settings = load_settings()
    return render_template("admin.html", settings=settings)
