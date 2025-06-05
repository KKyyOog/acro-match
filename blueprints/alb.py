from flask import Blueprint, request, render_template
from utils.sheets import (
    get_sheet,
    load_settings,
    update_liff_id_in_user_map  # ✅ 追加
)
from utils.liff import get_liff_id

alb_bp = Blueprint('alb', __name__)

@alb_bp.route("/register_alb")
def register_alb():
    settings = load_settings()
    liff_id = get_liff_id("alb")
    error_msg = request.args.get("error")
    return render_template("form_alb.html", settings=settings, liff_id=liff_id, error_msg=error_msg)

@alb_bp.route("/submit_alb", methods=["POST"])
def submit_alb():
    try:
        settings = load_settings()
        sheet = get_sheet("アルバイト登録シート")

        # LIFF ID -> Webhook ID 変換
        liff_user_id = request.form.get("user_id", "")
        true_user_id = liff_user_id

        # ヘッダーを更新
        sheet.delete_rows(1)
        headers = [
            settings.get("form_label_name", "名前"),
            settings.get("form_label_birthday4", "生年月日（月日4桁・例：0602）"),
            settings.get("form_label_alb_experience", "経験（複数選択可）"),
            settings.get("form_label_alb_handslevel", "補助レベル（複数選択可）"),
            settings.get("form_label_area", "希望エリア"),
            settings.get("form_label_available", "稼働可能日・時間"),
            settings.get("form_label_reachtime", "連絡可能時間帯")
        ]
        for field in settings.get("custom_fields", []):
            headers.append(field.get("label", ""))
        headers.append("user_id")
        sheet.insert_row(headers, index=1)

        # フォームデータ取得
        name = request.form.get("name", "")
        birthday4 = request.form.get("birthday4", "")  # ✅ 追加
        experience_list = request.form.getlist("experience")
        experience_str = ", ".join(experience_list)
        area = request.form.get("area", "")
        available = request.form.get("available", "")
        reachtime = request.form.get("reachtime", "")

        custom_values = [request.form.get(field.get("name", ""), "") for field in settings.get("custom_fields", [])]

        # ✅ LIFF ID と Webhook ID のマッピングを更新（ユーザーIDマップ）
        update_liff_id_in_user_map(name, birthday4, liff_user_id)

        # スプレッドシートに登録
        row = [name, experience_str, area, available, reachtime] + custom_values + [true_user_id]
        sheet.append_row(row)

        return "登録が完了しました！"
    except Exception as e:
        print(f"submit_alb エラー: {e}")
        return "Internal Server Error", 500
