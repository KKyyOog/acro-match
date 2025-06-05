# blueprints/admin.py
from flask import Blueprint, request, render_template, redirect
import json
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

SETTINGS_PATH = "settings.json"

def load_settings():
    try:
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print("⚠️ 設定読み込み失敗:", e)
    return {}

@admin_bp.route("/", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        settings = {
            "form_title": request.form.get("form_title", ""),
            "form_button_color": request.form.get("form_button_color", ""),
            "form_label_name": request.form.get("form_label_name", ""),
            "form_label_area": request.form.get("form_label_area", ""),
            "form_label_available": request.form.get("form_label_available", ""),
            "classroom_title": request.form.get("classroom_title", ""),
            "form_label_classroom_name": request.form.get("form_label_classroom_name", ""),
            "form_label_classroom_location": request.form.get("form_label_classroom_location", ""),
            "form_label_classroom_date": request.form.get("form_label_classroom_date", ""),
            "form_label_classroom_experience": request.form.get("form_label_classroom_experience", "")
        }

        settings["custom_fields_form"] = [
            {"label": request.form.get(f"custom_form_label_{i}"), "name": request.form.get(f"custom_form_name_{i}")}
            for i in range(1, int(request.form.get("custom_form_count", 0)) + 1)
            if request.form.get(f"custom_form_label_{i}") and request.form.get(f"custom_form_name_{i}")
        ]

        settings["custom_fields_classroom"] = [
            {"label": request.form.get(f"custom_classroom_label_{i}"), "name": request.form.get(f"custom_classroom_name_{i}")}
            for i in range(1, int(request.form.get("custom_classroom_count", 0)) + 1)
            if request.form.get(f"custom_classroom_label_{i}") and request.form.get(f"custom_classroom_name_{i}")
        ]

        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

        return redirect("/admin")

    return render_template("admin.html", settings=load_settings())