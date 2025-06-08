# blueprints/link.py
from flask import Blueprint, request
from utils.sheets import update_liff_id_by_name_and_birthday4
from utils.logging_util import log_exception

link_bp = Blueprint("link", __name__, url_prefix="/link")

@link_bp.route("/liff", methods=["POST"])
def link_liff_id():
    try:
        data = request.get_json()
        name = data.get("nickname")
        birthday4 = data.get("birthday4")
        liff_id = data.get("liff_id")

        if update_liff_id_by_name_and_birthday4(name, birthday4, liff_id):
            return "LIFF ID 登録完了", 200
        return "該当ユーザーが見つかりません", 404
    except Exception as e:
        log_exception(e, context="LIFF IDリンク処理")
        return "Internal Server Error", 500
