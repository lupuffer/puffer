from datetime import datetime

from flask import Blueprint, jsonify, request

from models import Book, Order, User, db
from system_notifications import notify_seller_order_created
from .orders_helpers import (
    ACTIVE_STATUSES,
    error_response,
    require_user,
    success_response,
)

orders_bp = Blueprint('orders', __name__)


@orders_bp.route('/api/orders', methods=['GET'])
def get_orders():
    user, err = require_user()
    if err:
        return err

    order_type = request.args.get('type', 'all')
    book_id = request.args.get('book_id')
    query = Order.query

    if book_id:
        query = query.filter_by(book_id=book_id).filter(
            db.or_(Order.buyer_id == user.id, Order.seller_id == user.id)
        )
    elif order_type == 'buyer':
        query = query.filter_by(buyer_id=user.id)
    elif order_type == 'seller':
        query = query.filter_by(seller_id=user.id)
    else:
        query = query.filter(
            db.or_(Order.buyer_id == user.id, Order.seller_id == user.id)
        )

    orders = query.order_by(Order.created_at.desc()).all()
    return success_response([order.to_dict(user.id) for order in orders])


@orders_bp.route('/api/orders', methods=['POST'])
def create_order():
    user, err = require_user()
    if err:
        return err

    data = request.get_json() or {}
    book_id = data.get('bookId')
    price = data.get('price')
    requested_buyer_id = str(data.get('buyerId') or '').strip() or None
    requested_seller_id = str(data.get('sellerId') or '').strip() or None

    if not book_id or price is None:
        return error_response('需要 bookId 和 price')

    book = db.session.get(Book, book_id)
    if not book:
        return error_response('书籍不存在', 404)

    seller_id = str(book.seller_id)
    if requested_seller_id and requested_seller_id != seller_id:
        return error_response('卖家信息与书籍不匹配', 400)

    active_order = Order.query.filter(
        Order.book_id == book_id,
        Order.status.in_(list(ACTIVE_STATUSES)),
    ).first()
    if active_order:
        requested_participants = {
            participant
            for participant in [requested_buyer_id, requested_seller_id]
            if participant
        }
        actual_participants = {active_order.buyer_id, active_order.seller_id}
        if user.id in actual_participants or requested_participants.issubset(actual_participants):
            return success_response(active_order.to_dict(user.id), '已找到进行中的订单')
        return error_response('书籍已有进行中的订单', 400)

    if book.status != 'on_sale':
        return error_response('书籍不可购买', 400)

    if user.id == seller_id:
        if not requested_buyer_id:
            return error_response('卖家发起订单时需要买家信息', 400)
        if requested_buyer_id == user.id:
            return error_response('不能与自己创建订单', 400)
        buyer = db.session.get(User, requested_buyer_id)
        if not buyer:
            return error_response('买家不存在', 404)
        buyer_id = buyer.id
    else:
        if requested_buyer_id and requested_buyer_id != user.id:
            return error_response('买家信息与当前登录用户不一致', 400)
        buyer_id = user.id

    if buyer_id == seller_id:
        return error_response('不能购买自己的书', 400)

    try:
        requested_price = float(price)
    except (TypeError, ValueError):
        requested_price = 0

    resolved_price = requested_price if requested_price > 0 else float(book.price or 0)
    if resolved_price <= 0:
        return error_response('订单金额无效', 400)

    order_id = f'ORDER{datetime.now().strftime("%Y%m%d%H%M%S")}{buyer_id[-3:]}'
    order = Order(
        id=order_id,
        book_id=book_id,
        buyer_id=buyer_id,
        seller_id=seller_id,
        price=resolved_price,
        final_price=resolved_price,
        status='created',
        trade_method='face',
        campus=book.campus,
    )

    try:
        db.session.add(order)
        book.status = 'reserved'
        book.updated_at = datetime.utcnow()
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return error_response(f'订单创建失败: {exc}', 500)

    if user.id != seller_id:
        try:
            notify_seller_order_created(book, order)
        except Exception as exc:
            db.session.rollback()
            print(f'order notification failed for order {order.id}: {exc}')

    return success_response(order.to_dict(user.id), '订单创建成功')