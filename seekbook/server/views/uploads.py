import os
import uuid
from flask import Blueprint, jsonify, request, current_app
from werkzeug.utils import secure_filename

from auth_utils import get_auth_error_response, get_request_user

uploads_bp = Blueprint('uploads', __name__)

ALLOWED_IMAGE_PREFIX = 'image/'


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), code


def require_user():
    user = get_request_user()
    if not user:
        return None, get_auth_error_response()
    return user, None


def _save_upload(file_storage):
    filename = secure_filename(file_storage.filename or '')
    if not filename:
        filename = f'upload_{uuid.uuid4().hex}'
    name, ext = os.path.splitext(filename)
    if not ext:
        ext = ''
    unique_name = f'{uuid.uuid4().hex}{ext}'
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    saved_path = os.path.join(upload_dir, unique_name)
    file_storage.save(saved_path)
    return f'/uploads/{unique_name}', unique_name, os.path.getsize(saved_path)


@uploads_bp.route('/api/upload', methods=['POST'])
def upload_file():
    user, error = require_user()
    if error:
        return error

    if 'file' not in request.files:
        return error_response('请上传文件', 400)

    file = request.files['file']
    if file.filename == '':
        return error_response('文件名不能为空', 400)

    url, saved_name, size = _save_upload(file)
    return success_response({
        'url': url,
        'name': saved_name,
        'originalName': file.filename,
        'size': size,
    }, '上传成功')


@uploads_bp.route('/api/upload/image', methods=['POST'])
def upload_image():
    user, error = require_user()
    if error:
        return error

    if 'file' not in request.files:
        return error_response('请上传图片文件', 400)

    file = request.files['file']
    if file.filename == '':
        return error_response('图片文件名不能为空', 400)

    if not file.mimetype.startswith(ALLOWED_IMAGE_PREFIX):
        return error_response('只支持图片文件上传', 400)

    url, saved_name, size = _save_upload(file)
    return success_response({
        'url': url,
        'name': saved_name,
        'originalName': file.filename,
        'size': size,
    }, '图片上传成功')
