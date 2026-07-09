import json
from datetime import datetime

from . import db


class CreditAudit(db.Model):
    __tablename__ = 'credit_audits'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False, index=True)
    trigger_type = db.Column(db.String(50), nullable=False)
    trigger_ref = db.Column(db.String(100), nullable=True)
    total_score = db.Column(db.Integer, nullable=False)
    completion_score = db.Column(db.Float, nullable=False, default=100.0)
    behavior_score = db.Column(db.Float, nullable=False)
    response_score = db.Column(db.Float, nullable=False)
    rating_score = db.Column(db.Float, nullable=False)
    metrics_json = db.Column(db.Text, nullable=False, default='{}')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        try:
            metrics = json.loads(self.metrics_json or '{}')
        except (TypeError, ValueError):
            metrics = {}

        return {
            'id': self.id,
            'userId': self.user_id,
            'triggerType': self.trigger_type,
            'triggerRef': self.trigger_ref,
            'totalScore': self.total_score,
            'completionScore': self.completion_score,
            'behaviorScore': self.behavior_score,
            'responseScore': self.response_score,
            'ratingScore': self.rating_score,
            'metrics': metrics,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
