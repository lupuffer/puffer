"""书籍草稿独立模块（利用Book表status='draft'存储）"""

import json

from flask import Blueprint, jsonify, request
from models import Book, db
from auth_utils import get_auth_error_response, get_request_user

drafts_bp = Blueprint('drafts', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), code


def require_user():
    user = get_request_user()
    if not user:
        return None, get_auth_error_response()
    return user, None


@drafts_bp.route('/api/books/drafts', methods=['GET'])
def get_drafts():
    """获取当前用户的草稿列表"""
    user, err = require_user()
    if err:
        return err

    drafts = Book.query.filter_by(seller_id=user.id, status='draft').order_by(Book.updated_at.desc()).all()
    return success_response([d.to_dict() for d in drafts])


@drafts_bp.route('/api/books/drafts', methods=['POST'])
def save_draft():
    """保存/新建草稿"""
    user, err = require_user()
    if err:
        return err

    data = request.get_json() or {}
    draft_id = data.get('draftId')

    if draft_id:
        # 更新已有草稿
        draft = db.session.get(Book, draft_id)
        if not draft or draft.seller_id != user.id:
            return error_response('草稿不存在', 404)
    else:
        draft = Book(seller_id=user.id, status='draft')

    draft.title = data.get('title', draft.title if draft_id else '').strip() or '(未命名草稿)'
    draft.author = data.get('author', '').strip()
    draft.publisher = data.get('publisher', '').strip()
    draft.edition = data.get('edition', '').strip()
    draft.isbn = data.get('isbn', '').strip()
    draft.condition = data.get('condition', 'like-new')
    draft.has_notes = bool(data.get('hasNotes', False))
    draft.price = float(data.get('price', 0) or 0)
    draft.original_price = float(data['originalPrice']) if data.get('originalPrice') else None
    draft.trade_method = data.get('tradeMethod', 'face')
    draft.campus = data.get('campus', 'zijingang')
    draft.contact = data.get('contact', '').strip()
    draft.images = json.dumps(data.get('images', []) or [])
    draft.tags = data.get('tags', '').strip()
    draft.description = data.get('description', '').strip()

    db.session.add(draft)
    db.session.commit()

    return success_response(draft.to_dict(), '草稿已保存')


@drafts_bp.route('/api/books/drafts/<int:draft_id>', methods=['DELETE'])
def delete_draft(draft_id):
    """删除草稿"""
    user, err = require_user()
    if err:
        return err

    draft = db.session.get(Book, draft_id)
    if not draft or draft.seller_id != user.id or draft.status != 'draft':
        return error_response('草稿不存在', 404)

    db.session.delete(draft)
    db.session.commit()
    return success_response({'id': draft_id}, '草稿已删除')