from flask import Blueprint, request
from utils.sheets import update_liff_id_in_user_map

link_bp = Blueprint("link", __name__)

@link_bp.route("/link_liff_id", methods=["POST"])
def link_liff_id():
    data = request.get_json()
    nickname = data.get("nickname")
    birthday4 = data.get("birthday4")
    liff_id = data.get("liff_id")

    if update_liff_id_in_user_map(nickname, birthday4, liff_id):
        return "LIFF ID 登録完了", 200
    else:
        return "該当ユーザーが見つかりません", 404
