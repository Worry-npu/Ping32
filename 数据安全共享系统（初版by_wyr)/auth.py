from flask import Blueprint, request, jsonify
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return jsonify({"success": True, "message": "登录成功", "token": user.username})
    else:
        return jsonify({"success": False, "message": "用户名或密码错误"}), 401


def verify_token(token):
    if not token:
        return None
    return User.query.filter_by(username=token).first()
