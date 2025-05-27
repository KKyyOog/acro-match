from flask import Blueprint, request, render_template
from utils.sheets import get_sheet, load_settings
from utils.liff import get_liff_id

alb_bp = Blueprint('alb', __name__)

# ヘッダーを自動で書き換える関数
def update_sheet_headers_for_alb(sheet, settings):
    headers = [
        settings.get("form_label_name", "名前"),
        settings.get("form_label_alb_experience", "経験"),
        settings.get("form_label_area", "希望エリア"),
        settings.get("form_label_available", "稼働可能日・時間"),
        settings.get("form_label_reachtime", "連絡可能時間帯"),
    ]

    # カスタム項目のラベルを追加
    for field in settings.get("custom_fields", []):
        headers.append(field.get("label", ""))

    headers.append("user_id")

    # 1行目を更新（古いヘッダー削除→新しいヘッダー追加）
    sheet.delete_rows(1)
    sheet.insert_row(headers, index=1)

@alb_bp.route("/register_alb")
def register_alb():
    settings = load_settings()
    liff_id = get_liff_id("alb")
    return render_template("form_alb.html", settings=settings, liff_id=liff_id)

@alb_bp.route("/submit_alb", methods=["POST"])
def submit_alb():
    try:
        settings = load_settings()
        sheet = get_sheet("アルバイト登録シート")

        # ヘッダーを更新
        update_sheet_headers_for_alb(sheet, settings)

        # フォームデータ取得
        name = request.form.get("name", "")
        experience_list = request.form.getlist("experience")
        experience_str = ", ".join(experience_list)
        area = request.form.get("area", "")
        available = request.form.get("available", "")
        user_id = request.form.get("user_id", "")

        # カスタム項目の値
        custom_values = [
            request.form.get(field.get("name", ""), "")
            for field in settings.get("custom_fields", [])
        ]

        # 書き込む1行分のデータ
        row = [name, experience_str, area, available] + custom_values + [user_id]
        sheet.append_row(row)

        return "登録が完了しました！"
    except Exception as e:
        print(f"submit_alb エラー: {e}")
        return "Internal Server Error", 500
