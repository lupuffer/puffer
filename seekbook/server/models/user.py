from datetime import datetime

from . import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=True, index=True)
    name = db.Column(db.String(100), nullable=False)
    college = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(50), nullable=True)
    campus = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    avatar = db.Column(db.String(500), nullable=True)
    role = db.Column(db.String(20), default='buyer')
    reputation = db.Column(db.String(10), default='A')
    credit_score = db.Column(db.Integer, default=100)
    points_balance = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    books = db.relationship('Book', backref='seller', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    shortage_registrations = db.relationship('ShortageRegistration', backref='user', lazy=True, cascade='all, delete-orphan')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy=True)
    revoked_tokens = db.relationship('RevokedToken', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'college': self.college,
            'grade': self.grade,
            'campus': self.campus,
            'phone': self.phone,
            'avatar': self.avatar,
            'role': self.role,
            'reputation': self.reputation,
            'creditScore': self.credit_score if self.credit_score is not None else 100,
            'pointsBalance': self.points_balance or 0,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
