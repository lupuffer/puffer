from datetime import datetime

from . import db


STATUS_LABELS = {
    'created': '待沟通',
    'negotiating': '协商中',
    'confirmed': '待见面',
    'completed': '已完成',
    'cancelled': '已取消',
}

TRADE_METHOD_LABELS = {
    'face': '当面交易',
    'mail': '邮寄',
    'both': '皆可',
}


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(50), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    buyer_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)

    price = db.Column(db.Float, nullable=False)
    final_price = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='created')

    trade_method = db.Column(db.String(20), nullable=True)
    campus = db.Column(db.String(100), nullable=True)
    contact_info = db.Column(db.String(500), nullable=True)

    meet_time = db.Column(db.String(100), nullable=True)
    meet_place = db.Column(db.String(200), nullable=True)

    tracking_number = db.Column(db.String(100), nullable=True)
    shipping_address = db.Column(db.String(500), nullable=True)

    buyer_rating = db.Column(db.Integer, nullable=True)
    seller_rating = db.Column(db.Integer, nullable=True)
    buyer_comment = db.Column(db.Text, nullable=True)
    seller_comment = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    cancelled_by = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=True)
    cancelled_from_status = db.Column(db.String(20), nullable=True)
    buyer_completed_confirmed = db.Column(db.Boolean, default=False)
    seller_completed_confirmed = db.Column(db.Boolean, default=False)

    book = db.relationship('Book', backref='orders')
    buyer = db.relationship('User', foreign_keys=[buyer_id], lazy='joined')
    seller = db.relationship('User', foreign_keys=[seller_id], lazy='joined')

    def get_status_label(self, current_role=None):
        if self.status != 'confirmed':
            return STATUS_LABELS.get(self.status, '未知状态')

        buyer_confirmed = bool(self.buyer_completed_confirmed)
        seller_confirmed = bool(self.seller_completed_confirmed)

        if buyer_confirmed and seller_confirmed:
            return STATUS_LABELS.get('completed', '已完成')

        if current_role == 'buyer':
            if buyer_confirmed and not seller_confirmed:
                return '待对方确认完成'
            if seller_confirmed and not buyer_confirmed:
                return '待你确认完成'
        elif current_role == 'seller':
            if seller_confirmed and not buyer_confirmed:
                return '待对方确认完成'
            if buyer_confirmed and not seller_confirmed:
                return '待你确认完成'

        return '待双方确认完成'

    def to_dict(self, current_user_id=None):
        current_role = None
        if current_user_id == self.buyer_id:
            current_role = 'buyer'
        elif current_user_id == self.seller_id:
            current_role = 'seller'

        partner = self.seller if current_role == 'buyer' else self.buyer
        partner_role = 'seller' if current_role == 'buyer' else 'buyer'
        buyer_completed_confirmed = bool(self.buyer_completed_confirmed)
        seller_completed_confirmed = bool(self.seller_completed_confirmed)
        current_user_completion_confirmed = None
        partner_completion_confirmed = None

        if current_role == 'buyer':
            current_user_completion_confirmed = buyer_completed_confirmed
            partner_completion_confirmed = seller_completed_confirmed
        elif current_role == 'seller':
            current_user_completion_confirmed = seller_completed_confirmed
            partner_completion_confirmed = buyer_completed_confirmed

        return {
            'id': self.id,
            'bookId': self.book_id,
            'buyerId': self.buyer_id,
            'sellerId': self.seller_id,
            'book': self.book.to_dict() if self.book else None,
            'buyer': self.buyer.to_dict() if self.buyer else None,
            'seller': self.seller.to_dict() if self.seller else None,
            'partner': partner.to_dict() if partner else None,
            'partnerRole': partner_role if current_role else None,
            'currentUserRole': current_role,
            'price': self.price,
            'finalPrice': self.final_price,
            'status': self.status,
            'statusLabel': self.get_status_label(current_role),
            'tradeMethod': self.trade_method,
            'tradeMethodLabel': TRADE_METHOD_LABELS.get(self.trade_method, self.trade_method or '未设置'),
            'campus': self.campus,
            'contactInfo': self.contact_info,
            'meetTime': self.meet_time,
            'meetPlace': self.meet_place,
            'buyerCompletedConfirmed': buyer_completed_confirmed,
            'sellerCompletedConfirmed': seller_completed_confirmed,
            'currentUserCompletionConfirmed': current_user_completion_confirmed,
            'partnerCompletionConfirmed': partner_completion_confirmed,
            'canCompleteOrder': self.status == 'confirmed' and current_user_completion_confirmed is False,
            'trackingNumber': self.tracking_number,
            'shippingAddress': self.shipping_address,
            'buyerRating': self.buyer_rating,
            'sellerRating': self.seller_rating,
            'buyerComment': self.buyer_comment,
            'sellerComment': self.seller_comment,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'confirmedAt': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None,
            'cancelledAt': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancelledBy': self.cancelled_by,
            'cancelledFromStatus': self.cancelled_from_status,
        }
