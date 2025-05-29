from flask import Blueprint, request, jsonify, send_file
import os
import logging
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime
from models import db, AuditLog, User
from auth import verify_token
from crypto_manager import CryptoManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('FileHandler')

file_bp = Blueprint('file', __name__)
UPLOAD_FOLDER = 'secure_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化加密管理器
crypto_mgr = CryptoManager()


def log_operation(user_id, action, filename):
    """安全记录审计日志"""
    try:
        # 修复：确保文件名长度不超过数据库限制
        truncated_filename = filename[:100] if len(filename) > 100 else filename

        log = AuditLog(
            user_id=user_id,
            action=action,
            filename=truncated_filename,
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"日志记录失败: {str(e)}")
        db.session.rollback()
        return False


@file_bp.route('/api/upload', methods=['POST'])
def upload_file():
    """修复的文件上传接口"""
    # 身份验证
    token = request.headers.get('Authorization')
    user = verify_token(token)
    if not user:
        return jsonify({"success": False, "message": "未授权"}), 401

    # 文件校验
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "未选择文件"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "无效文件名"}), 400

    try:
        # 获取原始文件名
        original_filename = file.filename
        safe_filename = secure_filename(original_filename)

        # 读取文件内容
        file_data = file.read()
        if len(file_data) == 0:
            return jsonify({"success": False, "message": "空文件无法上传"}), 400

        # 加密处理
        encryptor = crypto_mgr.get_encryptor()
        encrypted_data = encryptor.encrypt(file_data)

        # 存储加密文件
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
        with open(filepath, 'wb') as f:
            f.write(encrypted_data)

        # 记录审计日志
        log_operation(user.id, "上传", original_filename)

        return jsonify({
            "success": True,
            "message": "文件上传成功",
            "filename": original_filename,
            "algorithm": crypto_mgr.current_algorithm,
            "size": len(file_data),
            "encrypted_size": len(encrypted_data)
        })

    except Exception as e:
        logger.error(f"上传失败: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"文件上传失败: {str(e)}"
        }), 500


@file_bp.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    """修复的文件下载接口"""
    # 身份验证
    token = request.headers.get('Authorization')
    user = verify_token(token)
    if not user:
        return jsonify({"success": False, "message": "未授权"}), 401

    try:
        # 安全文件名处理
        safe_filename = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)

        if not os.path.exists(filepath):
            return jsonify({"success": False, "message": "文件不存在"}), 404

        # 读取加密文件
        with open(filepath, 'rb') as f:
            encrypted_data = f.read()

        if len(encrypted_data) == 0:
            return jsonify({"success": False, "message": "文件内容为空"}), 400

        # 解密处理
        encryptor = crypto_mgr.get_encryptor()
        decrypted_data = encryptor.decrypt(encrypted_data)

        if len(decrypted_data) == 0:
            return jsonify({"success": False, "message": "解密失败，返回空数据"}), 500

        # 记录审计日志
        log_operation(user.id, "下载", filename)

        # 返回文件流
        file_stream = BytesIO(decrypted_data)
        file_stream.seek(0)
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )

    except Exception as e:
        logger.error(f"下载失败: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"文件下载失败: {str(e)}"
        }), 500


@file_bp.route('/api/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """修复的文件删除接口"""
    token = request.headers.get('Authorization')
    user = verify_token(token)
    if not user:
        return jsonify({"success": False, "message": "未授权"}), 401

    try:
        safe_filename = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)

        if not os.path.exists(filepath):
            return jsonify({"success": False, "message": "文件不存在"}), 404

        # 删除文件
        os.remove(filepath)

        # 记录审计日志
        log_operation(user.id, "删除", filename)

        return jsonify({
            "success": True,
            "message": "文件已永久删除",
            "filename": filename
        })

    except Exception as e:
        logger.error(f"删除失败: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"文件删除失败: {str(e)}"
        }), 500


@file_bp.route('/api/files', methods=['GET'])
def list_files():
    """修复的文件列表接口"""
    token = request.headers.get('Authorization')
    user = verify_token(token)
    if not user:
        return jsonify({"success": False, "message": "未授权"}), 401

    try:
        # 获取所有上传记录
        upload_logs = AuditLog.query.filter_by(action='上传').order_by(AuditLog.timestamp.desc()).all()

        # 构建唯一文件列表
        file_map = {}
        for log in upload_logs:
            if log.filename not in file_map:
                filepath = os.path.join(UPLOAD_FOLDER, secure_filename(log.filename))
                if os.path.exists(filepath):
                    uploader = User.query.get(log.user_id)
                    file_size = os.path.getsize(filepath)
                    file_map[log.filename] = {
                        "filename": log.filename,
                        "upload_time": log.timestamp,
                        "uploader": uploader.username if uploader else "未知用户",
                        "size": file_size
                    }

        # 格式转换
        file_list = [{
            "filename": info["filename"],
            "upload_time": info["upload_time"].strftime('%Y-%m-%d %H:%M'),
            "uploader": info["uploader"],
            "size": info["size"]
        } for info in file_map.values()]

        return jsonify({
            "success": True,
            "files": file_list
        })

    except Exception as e:
        logger.error(f"获取文件列表失败: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"获取文件列表失败: {str(e)}"
        }), 500


@file_bp.route('/api/logs', methods=['GET'])
def get_logs():
    """修复的日志查询接口"""
    token = request.headers.get('Authorization')
    user = verify_token(token)
    if not user:
        return jsonify({"success": False, "message": "未授权"}), 401

    try:
        # 安全获取日志（限制最大数量）
        logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()

        log_list = []
        for log in logs:
            uploader = User.query.get(log.user_id)
            log_list.append({
                "username": uploader.username if uploader else "未知用户",
                "action": log.action,
                "filename": log.filename,
                "timestamp": log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })

        return jsonify({
            "success": True,
            "logs": log_list
        })

    except Exception as e:
        logger.error(f"获取日志失败: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"获取日志失败: {str(e)}"
        }), 500


@file_bp.route('/api/set_algorithm', methods=['POST'])
def set_algorithm():
    """修复的算法切换接口"""
    token = request.headers.get('Authorization')
    user = verify_token(token)
    if not user or user.role != 'admin':
        return jsonify({"success": False, "message": "权限不足"}), 403

    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "无效请求数据"}), 400

        algorithm = data.get('algorithm', 'AES').upper()

        if algorithm not in ['AES', 'DES']:
            return jsonify({"success": False, "message": "不支持的加密算法"}), 400

        # 更新算法
        crypto_mgr.current_algorithm = algorithm

        # 记录审计日志
        log_operation(user.id, "设置算法", f"切换至{algorithm}")

        return jsonify({
            "success": True,
            "message": f"加密算法已切换为 {algorithm}"
        })

    except Exception as e:
        logger.error(f"算法切换失败: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"算法切换失败: {str(e)}"
        }), 500