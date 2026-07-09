from datetime import datetime

from flask import jsonify, request
from sqlalchemy.exc import IntegrityError

from models import KnowledgeCheckIn, KnowledgePointLedger, db

from . import knowledge_bp
from .utils import require_user, success_response, today_key

MAX_POINTS = 100
CHECKIN_REWARD = 5
UPLOAD_REWARD = 10


def _get_points_balance(user):
    return max(0, int(user.points_balance or 0))


def _set_points_balance(user, value):
    user.points_balance = max(0, min(MAX_POINTS, int(value or 0)))


def _append_ledger(user, action, delta, ref_type=None, ref_id=None, note=None):
    entry = KnowledgePointLedger(
        user_id=user.id,
        action=action,
        delta=int(delta),
        balance_after=_get_points_balance(user),
        reference_type=ref_type,
        reference_id=ref_id,
        note=note,
        created_at=datetime.utcnow(),
    )
    db.session.add(entry)
    return entry


def award_points(user, amount, action, ref_type=None, ref_id=None, note=None):
    current = _get_points_balance(user)
    next_val = min(MAX_POINTS, current + int(amount))
    actual = next_val - current
    _set_points_balance(user, next_val)
    entry = _append_ledger(user, action, actual, ref_type, ref_id, note) if actual else None
    return {
        'current': current,
        'next': next_val,
        'delta': actual,
        'capped': actual < int(amount),
        'entry': entry,
    }


def deduct_points(user, amount, action, ref_type=None, ref_id=None, note=None):
    current = _get_points_balance(user)
    amount = int(amount)
    if current < amount:
        return None
    _set_points_balance(user, current - amount)
    _append_ledger(user, action, -amount, ref_type, ref_id, note)
    return {'current': current, 'next': current - amount, 'delta': -amount}


def points_payload(user):
    today = today_key()
    checked = KnowledgeCheckIn.query.filter_by(user_id=user.id, checkin_date=today).first() is not None
    ledger = (
        KnowledgePointLedger.query.filter_by(user_id=user.id)
        .order_by(KnowledgePointLedger.created_at.desc(), KnowledgePointLedger.id.desc())
        .limit(20)
        .all()
    )
    return {
        'balance': _get_points_balance(user),
        'max': MAX_POINTS,
        'checkedInToday': checked,
        'ledger': [item.to_dict() for item in ledger],
    }


def reward_payload(reward):
    if not reward:
        return None

    entry = reward.get('entry')
    return {
        'current': reward.get('current', 0),
        'next': reward.get('next', 0),
        'delta': reward.get('delta', 0),
        'capped': bool(reward.get('capped', False)),
        'entry': entry.to_dict() if entry and hasattr(entry, 'to_dict') else None,
    }


def _already_checked_in_response(user):
    points = points_payload(user)
    reward = {
        'current': points['balance'],
        'next': points['balance'],
        'delta': 0,
        'capped': False,
        'entry': None,
    }
    return success_response({'reward': reward_payload(reward), 'points': points}, '今日已签到')


@knowledge_bp.route('/api/knowledge/points', methods=['GET'])
def get_points():
    user, err = require_user()
    if err:
        return err
    return success_response(points_payload(user))


@knowledge_bp.route('/api/knowledge/checkin', methods=['POST'])
def checkin():
    user, err = require_user()
    if err:
        return err

    today = today_key()
    if KnowledgeCheckIn.query.filter_by(user_id=user.id, checkin_date=today).first():
        return _already_checked_in_response(user)

    db.session.add(KnowledgeCheckIn(user_id=user.id, checkin_date=today))
    reward = award_points(user, CHECKIN_REWARD, 'daily_checkin', 'checkin', None, '每日签到')

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return _already_checked_in_response(user)

    return success_response({'reward': reward_payload(reward), 'points': points_payload(user)}, '签到成功')
