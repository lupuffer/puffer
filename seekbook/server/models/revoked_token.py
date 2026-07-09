from datetime import datetime

from . import db


class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(64), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False, index=True)
    token_type = db.Column(db.String(20), nullable=False, default='access')
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    revoked_reason = db.Column(db.String(50), nullable=True)
    revoked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
