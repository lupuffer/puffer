"""可复现的卖家信誉分计算与审计日志。"""

import json
from datetime import datetime, timedelta
from statistics import median

from models import ChatSession, CreditAudit, Message, Order, db

BEHAVIOR_WEIGHT = 0.0
RESPONSE_WEIGHT = 0.30
RATING_WEIGHT = 0.70
RESPONSE_WINDOW_DAYS = 30
MIN_RESPONSE_SAMPLES = 3
RATING_PRIOR_SCORE = 100.0
RATING_SMOOTHING_SAMPLES = 5

CREDIT_LABELS = [
    (90, '极好'),
    (80, '良好'),
    (70, '一般'),
    (60, '较差'),
]


def score_to_label(score):
    for threshold, label in CREDIT_LABELS:
        if score >= threshold:
            return label
    return '很差'


def _behavior_metrics(user_id):
    completed_count = Order.query.filter_by(seller_id=user_id, status='completed').count()
    cancelled_count = Order.query.filter_by(seller_id=user_id, status='cancelled').count()
    return 100.0, {
        'completedSales': completed_count,
        'cancelledOrders': cancelled_count,
        'countedInScore': False,
    }


def _response_score(minutes):
    if minutes <= 10:
        return 100.0
    if minutes <= 30:
        return 90.0
    if minutes <= 120:
        return 80.0
    if minutes <= 360:
        return 65.0
    if minutes <= 1440:
        return 45.0
    return 20.0


def _response_metrics(user_id, now):
    cutoff = now - timedelta(days=RESPONSE_WINDOW_DAYS)
    sessions = ChatSession.query.filter_by(seller_id=user_id, is_system_session=False).all()
    response_minutes = []

    for session in sessions:
        messages = (
            Message.query
            .filter(
                Message.session_id == session.id,
                Message.is_system.is_(False),
                Message.created_at >= cutoff,
            )
            .order_by(Message.created_at.asc())
            .all()
        )
        waiting_message = None
        for message in messages:
            if message.sender_id == session.buyer_id:
                if waiting_message is None:
                    waiting_message = message
                continue
            if message.sender_id == session.seller_id and waiting_message is not None:
                elapsed = (message.created_at - waiting_message.created_at).total_seconds() / 60
                response_minutes.append(max(0.0, elapsed))
                waiting_message = None

    if not response_minutes:
        return 100.0, {
            'windowDays': RESPONSE_WINDOW_DAYS,
            'minimumSamples': MIN_RESPONSE_SAMPLES,
            'sampleCount': 0,
            'medianMinutes': None,
            'dataStatus': 'insufficient',
        }

    median_minutes = round(float(median(response_minutes)), 2)
    if len(response_minutes) < MIN_RESPONSE_SAMPLES:
        return 100.0, {
            'windowDays': RESPONSE_WINDOW_DAYS,
            'minimumSamples': MIN_RESPONSE_SAMPLES,
            'sampleCount': len(response_minutes),
            'medianMinutes': median_minutes,
            'dataStatus': 'insufficient',
        }

    return _response_score(median_minutes), {
        'windowDays': RESPONSE_WINDOW_DAYS,
        'minimumSamples': MIN_RESPONSE_SAMPLES,
        'sampleCount': len(response_minutes),
        'medianMinutes': median_minutes,
        'dataStatus': 'measured',
    }


def _rating_metrics(user_id):
    ratings = [
        order.buyer_rating
        for order in Order.query.filter_by(seller_id=user_id, status='completed').all()
        if order.buyer_rating is not None
    ]
    if not ratings:
        return 100.0, {
            'ratingCount': 0,
            'averageRating': None,
            'rawScore': None,
            'smoothedScore': 100.0,
            'priorScore': RATING_PRIOR_SCORE,
            'smoothingSamples': RATING_SMOOTHING_SAMPLES,
            'dataStatus': 'insufficient',
        }

    average_rating = sum(ratings) / len(ratings)
    raw_score = average_rating / 5 * 100
    smoothed_score = (
        raw_score * len(ratings) + RATING_PRIOR_SCORE * RATING_SMOOTHING_SAMPLES
    ) / (len(ratings) + RATING_SMOOTHING_SAMPLES)
    return smoothed_score, {
        'ratingCount': len(ratings),
        'averageRating': round(average_rating, 2),
        'rawScore': round(raw_score, 2),
        'smoothedScore': round(smoothed_score, 2),
        'priorScore': RATING_PRIOR_SCORE,
        'smoothingSamples': RATING_SMOOTHING_SAMPLES,
        'dataStatus': 'smoothed' if len(ratings) < RATING_SMOOTHING_SAMPLES else 'measured',
    }


def calculate_credit_snapshot(user, now=None):
    now = now or datetime.utcnow()
    behavior_score, behavior_metrics = _behavior_metrics(user.id)
    response_score, response_metrics = _response_metrics(user.id, now)
    rating_score, rating_metrics = _rating_metrics(user.id)
    weighted_score = (
        behavior_score * BEHAVIOR_WEIGHT
        + response_score * RESPONSE_WEIGHT
        + rating_score * RATING_WEIGHT
    )
    total_score = int(weighted_score + 0.5)
    total_score = min(100, max(0, total_score))

    return {
        'totalScore': total_score,
        'label': score_to_label(total_score),
        'components': {
            'behavior': {'weight': BEHAVIOR_WEIGHT, 'score': round(behavior_score, 2), **behavior_metrics},
            'response': {'weight': RESPONSE_WEIGHT, 'score': round(response_score, 2), **response_metrics},
            'rating': {'weight': RATING_WEIGHT, 'score': round(rating_score, 2), **rating_metrics},
        },
        'calculatedAt': now.isoformat(),
    }


def recalc_credit_for_user(user, trigger_type='manual', trigger_ref=None):
    snapshot = calculate_credit_snapshot(user)
    user.credit_score = snapshot['totalScore']
    user.reputation = snapshot['label']

    components = snapshot['components']
    audit = CreditAudit(
        user_id=user.id,
        trigger_type=trigger_type,
        trigger_ref=str(trigger_ref) if trigger_ref is not None else None,
        total_score=snapshot['totalScore'],
        completion_score=components['behavior']['score'],
        behavior_score=components['behavior']['score'],
        response_score=components['response']['score'],
        rating_score=components['rating']['score'],
        metrics_json=json.dumps(snapshot, ensure_ascii=False, sort_keys=True),
    )
    db.session.add(audit)
    return snapshot
