"""订单评价/评分独立模块——接入信誉分数值系统"""
from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy import update
from models import Order, User, db
from auth_utils import get_auth_error_response, get_request_user
from .credit_utils import recalc_credit_for_user, score_to_label

orders_reviews_bp = Blueprint('orders_reviews', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), code


@orders_reviews_bp.route('/api/orders/<order_id>/rate', methods=['POST'])
def rate_order(order_id):
    """为已完成订单提交评分（1-5 星）并自动联动更新对方信誉分"""
    user = get_request_user()
    if not user:
        return get_auth_error_response()

    order = db.session.get(Order, order_id)
    if not order:
        return error_response('订单不存在', 404)
    if user.id not in (order.buyer_id, order.seller_id):
        return error_response('不是该订单的参与方', 403)
    if order.status != 'completed':
        return error_response('只能评价已完成的订单', 400)

    data = request.get_json() or {}
    rating_value = int(data.get('rating', 0) or 0)
    if rating_value < 1 or rating_value > 5:
        return error_response('评分范围为 1-5', 400)
    comment = (data.get('comment') or '').strip()[:500]
    partner = None

    try:
        if user.id == order.buyer_id:
            if order.buyer_rating is not None:
                return error_response('你已经评价过这笔订单，不能重复评价', 409)
            result = db.session.execute(
                update(Order)
                .where(Order.id == order.id, Order.buyer_rating.is_(None))
                .values(
                    buyer_rating=rating_value,
                    buyer_comment=comment or None,
                    updated_at=datetime.utcnow(),
                )
            )
        else:
            if order.seller_rating is not None:
                return error_response('你已经评价过这笔订单，不能重复评价', 409)
            result = db.session.execute(
                update(Order)
                .where(Order.id == order.id, Order.seller_rating.is_(None))
                .values(
                    seller_rating=rating_value,
                    seller_comment=comment or None,
                    updated_at=datetime.utcnow(),
                )
            )

        if result.rowcount != 1:
            db.session.rollback()
            return error_response('你已经评价过这笔订单，不能重复评价', 409)
        db.session.expire(order)

        partner_id = order.seller_id if user.id == order.buyer_id else order.buyer_id
        partner = db.session.get(User, partner_id)
        if partner and user.id == order.buyer_id:
            recalc_credit_for_user(
                partner,
                trigger_type='buyer_rating',
                trigger_ref=order.id,
            )
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return error_response(f'评价失败: {exc}', 500)

    order_dict = order.to_dict(user.id)
    if partner:
        order_dict['partnerCreditScore'] = partner.credit_score or 100
        order_dict['partnerCreditLabel'] = score_to_label(partner.credit_score or 100)

    return success_response(order_dict, '评价成功')
