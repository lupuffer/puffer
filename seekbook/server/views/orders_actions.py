from datetime import datetime

from flask import Blueprint, request

from models import Book, Order, User, db
from .credit_utils import recalc_credit_for_user
from .orders_helpers import (
    ALLOWED_STATUS_TRANSITIONS,
    error_response,
    get_completion_waiting_message,
    require_participant,
    success_response,
)

orders_actions_bp = Blueprint('orders_actions', __name__)


@orders_actions_bp.route('/api/orders/<order_id>/confirm_meet', methods=['POST'])
def confirm_meet(order_id):
    data = request.get_json() or {}
    meet_time = data.get('meetTime', '').strip()
    meet_place = data.get('meetPlace', '').strip()
    if not meet_time or not meet_place:
        return error_response('见面时间和地点不能为空')

    order = db.session.get(Order, order_id)
    if not order:
        return error_response('订单不存在', 404)

    user, err = require_participant(order)
    if err:
        return err

    if order.status not in ['created', 'negotiating']:
        return error_response(f'当前状态 {order.status} 无法确认')

    try:
        order.meet_time = meet_time
        order.meet_place = meet_place
        order.status = 'confirmed'
        order.buyer_completed_confirmed = False
        order.seller_completed_confirmed = False
        order.confirmed_at = datetime.utcnow()
        order.updated_at = datetime.utcnow()
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return error_response(f'确认失败: {exc}', 500)

    return success_response(order.to_dict(user.id), '见面方案确认成功')


@orders_actions_bp.route('/api/orders/<oid>/complete', methods=['POST'])
def complete_order(oid):
    order = db.session.get(Order, oid)
    if not order:
        return error_response('订单不存在', 404)

    user, err = require_participant(order)
    if err:
        return err

    if order.status != 'confirmed':
        return error_response('订单尚未确认见面方案')

    try:
        now = datetime.utcnow()

        if user.id == order.buyer_id:
            if order.buyer_completed_confirmed:
                return success_response(
                    order.to_dict(user.id),
                    get_completion_waiting_message(order, user.id),
                )
            order.buyer_completed_confirmed = True
        else:
            if order.seller_completed_confirmed:
                return success_response(
                    order.to_dict(user.id),
                    get_completion_waiting_message(order, user.id),
                )
            order.seller_completed_confirmed = True

        order.updated_at = now

        if order.buyer_completed_confirmed and order.seller_completed_confirmed:
            order.status = 'completed'
            order.completed_at = now
            if order.book:
                order.book.status = 'sold'
                order.book.updated_at = now
            seller = db.session.get(User, order.seller_id)
            if seller:
                recalc_credit_for_user(
                    seller,
                    trigger_type='order_completed',
                    trigger_ref=order.id,
                )

        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return error_response(f'完成订单失败: {exc}', 500)

    return success_response(
        order.to_dict(user.id),
        get_completion_waiting_message(order, user.id),
    )


@orders_actions_bp.route('/api/orders/<oid>/cancel', methods=['POST'])
def cancel_order(oid):
    order = db.session.get(Order, oid)
    if not order:
        return error_response('订单不存在', 404)

    user, err = require_participant(order)
    if err:
        return err

    if order.status == 'completed':
        return error_response('已完成的订单无法取消')

    try:
        from .orders_helpers import ACTIVE_STATUSES

        now = datetime.utcnow()
        previous_status = order.status
        order.status = 'cancelled'
        order.updated_at = now
        order.cancelled_at = now
        order.cancelled_by = user.id
        order.cancelled_from_status = previous_status
        if order.book and order.book.status == 'reserved':
            has_other_active_order = Order.query.filter(
                Order.book_id == order.book_id,
                Order.id != order.id,
                Order.status.in_(list(ACTIVE_STATUSES)),
            ).first()
            if not has_other_active_order:
                order.book.status = 'on_sale'
                order.book.updated_at = datetime.utcnow()
        seller = db.session.get(User, order.seller_id)
        if seller:
            is_seller_fault = previous_status == 'confirmed' and user.id == order.seller_id
            recalc_credit_for_user(
                seller,
                trigger_type='order_cancelled_recorded',
                trigger_ref=order.id,
            )
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return error_response(f'取消失败: {exc}', 500)

    return success_response(
        {'orderId': order.id, 'status': 'cancelled'}, '订单已取消'
    )


@orders_actions_bp.route('/api/orders/<oid>', methods=['GET'])
def get_order_detail(oid):
    order = db.session.get(Order, oid)
    if not order:
        return error_response('订单不存在', 404)

    user, err = require_participant(order)
    if err:
        return err

    return success_response(order.to_dict(user.id))


@orders_actions_bp.route('/api/orders/<oid>/status', methods=['PUT'])
def update_order_status(oid):
    order = db.session.get(Order, oid)
    if not order:
        return error_response('订单不存在', 404)

    user, err = require_participant(order)
    if err:
        return err

    data = request.get_json() or {}
    new_status = (data.get('status') or '').strip()

    valid_transitions = ALLOWED_STATUS_TRANSITIONS.get(order.status, set())
    if not valid_transitions:
        return error_response(f'当前状态 {order.status} 不允许变更', 400)
    if new_status not in valid_transitions:
        allowed_list = ', '.join(sorted(valid_transitions))
        return error_response(
            f'无法从 {order.status} 切换到 {new_status}，允许的操作：{allowed_list}',
            400,
        )

    try:
        previous_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()

        if new_status == 'cancelled':
            order.cancelled_at = order.updated_at
            order.cancelled_by = user.id
            order.cancelled_from_status = previous_status
            if order.book and order.book.status == 'reserved':
                from .orders_helpers import ACTIVE_STATUSES
                has_other_active = Order.query.filter(
                    Order.book_id == order.book_id,
                    Order.id != order.id,
                    Order.status.in_(list(ACTIVE_STATUSES)),
                ).first()
                if not has_other_active:
                    order.book.status = 'on_sale'
                    order.book.updated_at = datetime.utcnow()
            seller = db.session.get(User, order.seller_id)
            if seller:
                is_seller_fault = previous_status == 'confirmed' and user.id == order.seller_id
                recalc_credit_for_user(
                    seller,
                    trigger_type='order_cancelled_recorded',
                    trigger_ref=order.id,
                )
        elif new_status == 'completed':
            order.completed_at = order.updated_at
            if order.book:
                order.book.status = 'sold'
                order.book.updated_at = order.updated_at
            seller = db.session.get(User, order.seller_id)
            if seller:
                recalc_credit_for_user(
                    seller,
                    trigger_type='order_completed',
                    trigger_ref=order.id,
                )

        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        return error_response(f'状态更新失败: {exc}', 500)

    return success_response(order.to_dict(user.id), '订单状态已更新')
