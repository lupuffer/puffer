from datetime import datetime

from . import db


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.String(100), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    buyer_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    book_title = db.Column(db.String(200), nullable=True)
    preview = db.Column(db.String(500), default='')
    unread_count = db.Column(db.Integer, default=0)
    buyer_unread_count = db.Column(db.Integer, default=0)
    seller_unread_count = db.Column(db.Integer, default=0)
    is_system_session = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship('Message', backref='session', lazy=True, cascade='all, delete-orphan')
    book = db.relationship('Book', backref='chat_sessions')
    buyer = db.relationship('User', foreign_keys=[buyer_id], lazy='joined')
    seller = db.relationship('User', foreign_keys=[seller_id], lazy='joined')

    def to_dict(self, current_user_id=None):
        if self.is_system_session:
            counterpart = self.seller
            counterpart_role = 'system'
        elif current_user_id == self.seller_id:
            counterpart = self.buyer
            counterpart_role = 'buyer'
        elif current_user_id == self.buyer_id:
            counterpart = self.seller
            counterpart_role = 'seller'
        else:
            counterpart = self.seller or self.buyer
            counterpart_role = 'seller'

        unread = 0
        if current_user_id == self.seller_id:
            unread = self.seller_unread_count
        elif current_user_id == self.buyer_id:
            unread = self.buyer_unread_count

        return {
            'id': self.id,
            'bookId': self.book_id,
            'sellerId': self.seller_id,
            'buyerId': self.buyer_id,
            'price': self.book.price if self.book else None,
            'name': counterpart.name if counterpart else 'Unknown User',
            'avatar': counterpart.avatar if counterpart else None,
            'bookTitle': self.book_title,
            'preview': self.preview,
            'unread': unread,
            'role': counterpart_role,
            'isSystemSession': bool(self.is_system_session),
            'time': self.updated_at.strftime('%H:%M') if self.updated_at else '',
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(100), db.ForeignKey('chat_sessions.id'), nullable=False)
    sender_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    sender_role = db.Column(db.String(20), default='buyer')
    text = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')
    is_system = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self, current_user_id=None):
        return {
            'id': self.id,
            'sessionId': self.session_id,
            'senderId': self.sender_id,
            'senderRole': self.sender_role,
            'text': self.text,
            'type': 'sent' if current_user_id and self.sender_id == current_user_id else 'received',
            'messageType': self.message_type,
            'isSystem': self.is_system,
            'time': self.created_at.strftime('%H:%M') if self.created_at else '',
        }
