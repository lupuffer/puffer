from datetime import datetime

from flask import Blueprint, jsonify, request

from auth_utils import get_auth_error_response, get_request_user
from models import Book, ChatSession, Message, User, db
from .credit_utils import recalc_credit_for_user

chats_bp = Blueprint('chats', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), code


def require_user():
    user = get_request_user()
    if not user:
        return None, get_auth_error_response()
    return user, None


@chats_bp.route('/api/chat/sessions', methods=['GET'])
def get_chat_sessions():
    user, error = require_user()
    if error:
        return error

    sessions = ChatSession.query.filter(
        db.or_(ChatSession.buyer_id == user.id, ChatSession.seller_id == user.id)
    ).order_by(ChatSession.updated_at.desc()).all()

    return success_response([session.to_dict(user.id) for session in sessions])


MAX_CHAT_MESSAGE_LENGTH = 2000


@chats_bp.route('/api/chat/sessions', methods=['POST'])
def create_chat_session():
    user, error = require_user()
    if error:
        return error

    data = request.get_json() or {}
    book_id = data.get('bookId')
    seller_id = str(data.get('sellerId') or '').strip()
    requested_buyer_id = str(data.get('buyerId') or '').strip()
    book_title = (data.get('bookTitle') or '').strip()

    if not book_id or not seller_id:
        return error_response('参数不完整')

    book = db.session.get(Book, book_id)
    if not book:
        return error_response('书籍不存在', 404)

    if str(book.seller_id) != seller_id:
        return error_response('卖家信息与书籍不匹配', 400)

    seller = db.session.get(User, seller_id)
    if not seller:
        return error_response('卖家不存在', 404)

    if seller_id == user.id:
        if not requested_buyer_id:
            return error_response('卖家发起会话时需要买家信息', 400)
        if requested_buyer_id == user.id:
            return error_response('不能与自己建立会话', 400)
        buyer = db.session.get(User, requested_buyer_id)
        if not buyer:
            return error_response('买家不存在', 404)
        buyer_id = buyer.id
    else:
        if requested_buyer_id and requested_buyer_id != user.id:
            return error_response('买家信息与当前登录用户不一致', 400)
        buyer_id = user.id

    session_id = f'session_{book_id}_{seller_id}_{buyer_id}'
    session = db.session.get(ChatSession, session_id)
    if not session:
        session = ChatSession(
            id=session_id,
            book_id=book_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            book_title=book_title[:200],
        )
        db.session.add(session)
        db.session.commit()

    return success_response(session.to_dict(user.id))


@chats_bp.route('/api/chat/sessions/<session_id>/messages', methods=['GET'])
def get_messages(session_id):
    user, error = require_user()
    if error:
        return error

    session = db.session.get(ChatSession, session_id)
    if not session:
        return error_response('会话不存在', 404)

    if session.buyer_id != user.id and session.seller_id != user.id:
        return error_response('无权访问此会话', 403)

    messages = Message.query.filter_by(session_id=session_id).order_by(Message.created_at).all()

    if user.id == session.seller_id:
        session.seller_unread_count = 0
    elif user.id == session.buyer_id:
        session.buyer_unread_count = 0

    db.session.commit()

    return success_response([message.to_dict(user.id) for message in messages])


@chats_bp.route('/api/chat/messages', methods=['POST'])
def send_message():
    user, error = require_user()
    if error:
        return error

    data = request.get_json() or {}
    session_id = data.get('sessionId')
    text = (data.get('text') or '').strip()

    if not session_id or not text:
        return error_response('参数不完整')

    if len(text) > MAX_CHAT_MESSAGE_LENGTH:
        return error_response(f'消息过长，最多 {MAX_CHAT_MESSAGE_LENGTH} 字符', 400)

    session = db.session.get(ChatSession, session_id)
    if not session:
        return error_response('会话不存在', 404)

    if session.buyer_id != user.id and session.seller_id != user.id:
        return error_response('无权发送消息', 403)

    if user.id == session.seller_id:
        sender_id = session.seller_id
        sender_role = 'seller'
    elif user.id == session.buyer_id:
        sender_id = session.buyer_id
        sender_role = 'buyer'
    else:
        return error_response('无权发送消息', 403)

    previous_message = (
        Message.query
        .filter_by(session_id=session_id, is_system=False)
        .order_by(Message.created_at.desc())
        .first()
    )

    message = Message(
        session_id=session_id,
        sender_id=sender_id,
        sender_role=sender_role,
        text=text,
        is_system=False,
    )
    db.session.add(message)

    is_measured_seller_reply = (
        user.id == session.seller_id
        and previous_message is not None
        and previous_message.sender_id == session.buyer_id
    )

    session.preview = text[:50] + '...' if len(text) > 50 else text
    session.updated_at = datetime.utcnow()
    if user.id == session.seller_id:
        session.buyer_unread_count += 1
    elif user.id == session.buyer_id:
        session.seller_unread_count += 1

    if is_measured_seller_reply:
        db.session.flush()
        seller = db.session.get(User, session.seller_id)
        if seller:
            recalc_credit_for_user(
                seller,
                trigger_type='seller_reply',
                trigger_ref=message.id or session.id,
            )

    db.session.commit()
    return success_response(message.to_dict(user.id), '消息发送成功')
