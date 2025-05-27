from flask import Blueprint, request, jsonify, send_file
import os
from werkzeug.utils import secure_filename
from models import db, AuditLog,User
from auth import verify_token
from cryptography.fernet import Fernet
from io import BytesIO


file_bp = Blueprint('file', __name__)
UPLOAD_FOLDER = 'uploads'
KEY_PATH = 'secret.key'

# 加载或创建密钥
if os.path.exists(KEY_PATH):
    with open(KEY_PATH, 'rb') as f:
        ENCRYPTION_KEY = f.read()
else:
    ENCRYPTION_KEY = Fernet.generate_key()
    with open(KEY_PATH, 'wb') as f:
        f.write(ENCRYPTION_KEY)

cipher = Fernet(ENCRYPTION_KEY)


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@file_bp.route('/api/upload', methods=['POST'])
def upload_file():
    token = request.headers.get('Authorization')
    user = verify_token(token)
    if not user:
        return jsonify({"success": False, "message": "未授权"}), 401

    if 'file' not in request.files:
        return jsonify({"success": False, "message": "没有文件"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    # 加密内容
    encrypted_data = cipher.encrypt(file.read())
    with open(filepath, 'wb') as f:
        f.write(encrypted_data)

    # 日志
    log = AuditLog(user_id=user.id, action="上传", filename=filename)
    db.session.add(log)
    db.session.commit()

    return jsonify({"success": True, "message": "上传成功"})

@file_bp.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    token = request.headers.get('Authorization')
    user = verify_token(token)
    if not user:
        return jsonify({"success": False, "message": "未授权"}), 401

    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({"success": False, "message": "文件不存在"}), 404

    # 读取并解密
    with open(filepath, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = cipher.decrypt(encrypted_data)

    # 用内存文件发送
    file_stream = BytesIO(decrypted_data)
    file_stream.seek(0)

    # 记录日志
    log = AuditLog(user_id=user.id, action="下载", filename=filename)
    db.session.add(log)
    db.session.commit()

    return send_file(
        file_stream,
        as_attachment=True,
        download_name=filename  # Flask 2.0+ 参数，旧版本用 attachment_filename
    )

# 删除
@file_bp.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    token = request.headers.get('Authorization')
    user = verify_token(token)
    if not user:
        return jsonify({"success": False, "message": "未授权"}), 401

    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({"success": False, "message": "文件不存在"}), 404

    # 删除文件
    os.remove(filepath)

    # 不删除上传日志，保留历史上传记录

    # 添加删除日志记录
    log = AuditLog(user_id=user.id, action="删除", filename=filename)
    db.session.add(log)
    db.session.commit()

    return jsonify({"success": True, "message": "文件已删除"})


# 文件列表
@file_bp.route('/api/files', methods=['GET'])
def list_files():
    token = request.headers.get('Authorization')
    user = verify_token(token)
    if not user:
        return jsonify({"success": False, "message": "未授权"}), 401

    file_logs = AuditLog.query.filter_by(action='上传').all()
    unique_files = {}
    for log in file_logs:
        if log.filename not in unique_files:
            filepath = os.path.join(UPLOAD_FOLDER, secure_filename(log.filename))
            if os.path.exists(filepath):  # ✅ 文件仍存在磁盘才加入
                unique_files[log.filename] = log

    file_list = [{
        "filename": log.filename,
        "upload_time": log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        "uploader": User.query.get(log.user_id).username
    } for log in unique_files.values()]

    return jsonify({"success": True, "files": file_list})

# 获得日志
@file_bp.route('/api/logs', methods=['GET'])
def get_logs():
    token = request.headers.get('Authorization')
    user = verify_token(token)
    if not user:
        return jsonify({"success": False, "message": "未授权"}), 401

    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    log_list = []
    for log in logs:
        username = User.query.get(log.user_id)
        username_str = username.username if username else "未知用户"
        timestamp_str = log.timestamp.strftime('%Y-%m-%d %H:%M:%S') if log.timestamp else ""
        log_list.append({
            "username": username_str,
            "action": log.action,
            "filename": log.filename,
            "timestamp": timestamp_str
        })

    return jsonify({"success": True, "logs": log_list})