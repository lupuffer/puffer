from flask import Blueprint, jsonify, request

from auth_utils import get_auth_error_response, get_request_user
from models import Book, Favorite, db

favorites_bp = Blueprint('favorites', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), code


def require_user():
    user = get_request_user()
    if not user:
        return None, get_auth_error_response()
    return user, None


@favorites_bp.route('/api/favorites', methods=['GET'])
def get_favorites():
    user, error = require_user()
    if error:
        return error

    favorite_books = Favorite.query.filter_by(user_id=user.id).all()
    return success_response([favorite.book_id for favorite in favorite_books])


@favorites_bp.route('/api/favorites', methods=['POST'])
def add_favorite():
    user, error = require_user()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    book_id = data.get('bookId')
    if book_id is None:
        return error_response('缺少 bookId 参数', 400)

    try:
        book_id = int(book_id)
    except (TypeError, ValueError):
        return error_response('bookId 必须为整数', 400)

    book = db.session.get(Book, book_id)
    if not book:
        return error_response('书籍不存在', 404)

    existing = Favorite.query.filter_by(user_id=user.id, book_id=book_id).first()
    if existing:
        return success_response({'bookId': book_id}, '已收藏')

    favorite = Favorite(user_id=user.id, book_id=book_id)
    db.session.add(favorite)
    db.session.commit()
    return success_response({'bookId': book_id}, '收藏成功')


@favorites_bp.route('/api/favorites/<int:book_id>', methods=['DELETE'])
def remove_favorite(book_id):
    user, error = require_user()
    if error:
        return error

    favorite = Favorite.query.filter_by(user_id=user.id, book_id=book_id).first()
    if not favorite:
        return success_response({'bookId': book_id}, '未收藏')

    db.session.delete(favorite)
    db.session.commit()
    return success_response({'bookId': book_id}, '取消收藏成功')


@favorites_bp.route('/api/favorites/<int:book_id>/check', methods=['GET'])
def check_favorite(book_id):
    user, error = require_user()
    if error:
        return error

    exists = Favorite.query.filter_by(user_id=user.id, book_id=book_id).first() is not None
    return success_response({'isFavorited': exists})
