from flask import Blueprint, request, render_template, redirect
from utils.sheets import load_settings, save_settings

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        new_settings = {
            "title": request.form.get("title"),
            "button_color": request.form.get("button_color"),
            "form_label_name": request.form.get("form_label_name"),
            "form_label_area": request.form.get("form_label_area"),
            "form_label_available": request.form.get("form_label_available"),
            "classroom_title": request.form.get("classroom_title"),
            "form_label_classroom_name": request.form.get("form_label_classroom_name"),
            "form_label_classroom_location": request.form.get("form_label_classroom_location"),
            "form_label_classroom_date": request.form.get("form_label_classroom_date"),
            "form_label_classroom_experience": request.form.get("form_label_classroom_experience"),
            "custom_fields": []
        }
        custom_count = int(request.form.get("custom_count", 0))
        for i in range(1, custom_count + 1):
            label = request.form.get(f"custom_label_{i}")
            name = request.form.get(f"custom_name_{i}")
            if label and name:
                new_settings["custom_fields"].append({"label": label, "name": name})
        save_settings(new_settings)
        return redirect('/admin')
    
    current_settings = load_settings()
    return render_template('admin.html', settings=current_settings)
