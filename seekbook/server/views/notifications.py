from datetime import datetime

from flask import Blueprint, jsonify
from models import db
from models.chat import Message
from auth_utils import get_auth_error_response, get_request_user

notifications_bp = Blueprint('notifications', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), code


def require_user():
    user = get_request_user()
    if not user:
        return None, get_auth_error_response()
    return user, None


@notifications_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    """获取用户的系统通知列表（缺货匹配等系统消息）"""
    user, error = require_user()
    if error:
        return error

    # 系统消息通过 chat session 中的 is_system=True 消息传递
    # 这里查询所有属于该用户的会话中的系统消息
    from models import ChatSession

    sessions = ChatSession.query.filter(
        ChatSession.is_system_session.is_(True),
        db.or_(
            ChatSession.buyer_id == user.id,
            ChatSession.seller_id == user.id,
        ),
    ).all()

    session_ids = [
        session.id
        for session in sessions
        if (
            session.buyer_id == user.id
            and (session.buyer_unread_count or 0) > 0
        ) or (
            session.seller_id == user.id
            and (session.seller_unread_count or 0) > 0
        )
    ]
    if not session_ids:
        return success_response([])

    system_messages = (
        Message.query
        .filter(
            Message.session_id.in_(session_ids),
            Message.is_system.is_(True),
        )
        .order_by(Message.created_at.desc())
        .limit(20)
        .all()
    )

    notifications = [
        {
            'id': msg.id,
            'text': msg.text,
            'time': msg.created_at.isoformat() if msg.created_at else '',
            'sessionId': msg.session_id,
            'read': False,
        }
        for msg in system_messages
    ]

    return success_response(notifications)
