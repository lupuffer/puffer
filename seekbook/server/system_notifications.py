import re
from datetime import datetime

from werkzeug.security import generate_password_hash

from models import ChatSession, Message, ShortageRegistration, User, db

SYSTEM_USER_ID = 'system_notice_bot'
SYSTEM_USERNAME = 'system_notice_bot'
SYSTEM_EMAIL = 'system_notice_bot@seekbook.local'
SYSTEM_NAME = '星图系统助手'
SYSTEM_AVATAR = 'https://api.dicebear.com/7.x/bottts/svg?seed=starbook-system'
SYSTEM_PASSWORD = 'SystemBot123'


def ensure_system_user():
    system_user = db.session.get(User, SYSTEM_USER_ID)
    if system_user:
        return system_user

    system_user = User(
        id=SYSTEM_USER_ID,
        username=SYSTEM_USERNAME,
        email=SYSTEM_EMAIL,
        name=SYSTEM_NAME,
        password_hash=generate_password_hash(SYSTEM_PASSWORD),
        avatar=SYSTEM_AVATAR,
        role='system',
        reputation='S',
        created_at=datetime.utcnow(),
    )
    db.session.add(system_user)
    db.session.commit()
    return system_user


def normalize_book_name(value):
    text = str(value or '').strip().lower()
    return re.sub(r'[^0-9a-z\u4e00-\u9fff]', '', text)


def is_matching_shortage(book, registration):
    registration_name = normalize_book_name(registration.book_name)
    book_name = normalize_book_name(book.title)

    if not registration_name or not book_name:
        return False

    registration_isbn = str(registration.isbn or '').replace('-', '').replace(' ', '')
    book_isbn = str(book.isbn or '').replace('-', '').replace(' ', '')
    if registration_isbn and book_isbn and registration_isbn == book_isbn:
        return True

    return registration_name == book_name or registration_name in book_name or book_name in registration_name


def build_shortage_message(book, registration):
    seller_name = book.seller.name if getattr(book, 'seller', None) else '有同学'
    lines = [
        f'你登记的《{registration.book_name}》已有匹配书籍上架。',
        f'当前书籍：《{book.title}》',
        f'卖家：{seller_name}',
        f'价格：¥{float(book.price or 0):.2f}',
    ]
    if book.campus:
        lines.append(f'校区：{book.campus}')
    lines.append('你可以前往星图集市查看详情并联系卖家。')
    return '\n'.join(lines)


def build_order_purchase_message(book, order):
    buyer_name = order.buyer.name if getattr(order, 'buyer', None) else '有买家'
    lines = [
        f'你的《{book.title}》已被买家下单，请前往“我的订单”查看。',
        f'订单编号：{order.id}',
        f'买家：{buyer_name}',
        f'成交金额：¥{float(order.final_price or order.price or 0):.2f}',
    ]
    if book.campus:
        lines.append(f'校区：{book.campus}')
    lines.append('如发现异常，可在“我的订单”中取消订单，书籍会重新上架。')
    return '\n'.join(lines)


def notify_seller_order_created(book, order):
    system_user = ensure_system_user()
    session_id = f'system_order_notice_{order.id}'
    if db.session.get(ChatSession, session_id):
        return

    message_text = build_order_purchase_message(book, order)
    session = ChatSession(
        id=session_id,
        book_id=book.id,
        buyer_id=book.seller_id,
        seller_id=system_user.id,
        book_title=(book.title or '')[:200],
        preview=message_text[:50] + ('...' if len(message_text) > 50 else ''),
        buyer_unread_count=1,
        seller_unread_count=0,
        is_system_session=True,
    )
    message = Message(
        session_id=session_id,
        sender_id=system_user.id,
        sender_role='system',
        text=message_text,
        message_type='system',
        is_system=True,
    )

    db.session.add(session)
    db.session.add(message)
    db.session.commit()


def notify_shortage_matches(book):
    system_user = ensure_system_user()
    waiting_registrations = (
        ShortageRegistration.query
        .filter_by(status='waiting')
        .order_by(ShortageRegistration.created_at.asc())
        .all()
    )

    created_any = False

    for registration in waiting_registrations:
        if registration.user_id == book.seller_id:
            continue
        if not is_matching_shortage(book, registration):
            continue

        session_id = f'system_shortage_{registration.id}_{book.id}'
        if db.session.get(ChatSession, session_id):
            continue

        message_text = build_shortage_message(book, registration)
        session = ChatSession(
            id=session_id,
            book_id=book.id,
            buyer_id=registration.user_id,
            seller_id=system_user.id,
            book_title=(book.title or '')[:200],
            preview=message_text[:50] + ('...' if len(message_text) > 50 else ''),
            buyer_unread_count=1,
            seller_unread_count=0,
            is_system_session=True,
        )
        message = Message(
            session_id=session_id,
            sender_id=system_user.id,
            sender_role='system',
            text=message_text,
            message_type='system',
            is_system=True,
        )

        db.session.add(session)
        db.session.add(message)
        created_any = True

    if created_any:
        db.session.commit()
