from flask import Blueprint, jsonify
from models import CreditAudit, Order, Book, db
from auth_utils import get_auth_error_response, get_request_user
from .credit_utils import calculate_credit_snapshot

user_stats_bp = Blueprint('user_stats', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), code


def require_user():
    user = get_request_user()
    if not user:
        return None, get_auth_error_response()
    return user, None


@user_stats_bp.route('/api/user/stats', methods=['GET'])
def get_user_stats():
    """返回用户统计数据：累计收益、交易统计与信誉分项。"""
    user, error = require_user()
    if error:
        return error

    # 累计收益 = 已完成订单的 final_price 总和（作为卖家的部分）
    completed_orders = Order.query.filter_by(seller_id=user.id, status='completed').all()
    total_earnings = sum(
        float(order.final_price or order.price or 0) for order in completed_orders
    )

    # 也可以计算作为买家花费
    bought_orders = Order.query.filter_by(buyer_id=user.id, status='completed').all()
    total_spent = sum(
        float(order.final_price or order.price or 0) for order in bought_orders
    )

    # 在售书籍数量
    on_sale_count = Book.query.filter_by(seller_id=user.id, status='on_sale').count()
    credit_snapshot = calculate_credit_snapshot(user)

    return success_response({
        'total_earnings': round(total_earnings, 2),
        'total_spent': round(total_spent, 2),
        'on_sale_count': on_sale_count,
        'completed_sales': len(completed_orders),
        'completed_purchases': len(bought_orders),
        'completed_transactions': len(completed_orders) + len(bought_orders),
        'credit_score': credit_snapshot['totalScore'],
        'reputation': credit_snapshot['label'],
        'credit_components': credit_snapshot['components'],
    })


@user_stats_bp.route('/api/user/credit-audits', methods=['GET'])
def get_credit_audits():
    user, error = require_user()
    if error:
        return error

    audits = (
        CreditAudit.query
        .filter_by(user_id=user.id)
        .order_by(CreditAudit.created_at.desc(), CreditAudit.id.desc())
        .limit(50)
        .all()
    )
    return success_response([audit.to_dict() for audit in audits])
