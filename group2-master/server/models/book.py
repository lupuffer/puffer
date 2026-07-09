from datetime import datetime
from . import db
import json

class Book(db.Model):
    """书籍表"""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=True)
    publisher = db.Column(db.String(200), nullable=True)
    edition = db.Column(db.String(100), nullable=True)
    isbn = db.Column(db.String(20), nullable=True)
    condition = db.Column(db.String(20), default='like-new')
    has_notes = db.Column(db.Boolean, default=False)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=True)
    trade_method = db.Column(db.String(20), default='face')
    campus = db.Column(db.String(100), default='zijingang')
    contact = db.Column(db.String(200), nullable=True)
    images = db.Column(db.Text, default='[]')
    tags = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    subject = db.Column(db.String(50), nullable=True)
    grade = db.Column(db.String(20), nullable=True)
    book_type = db.Column(db.String(20), default='textbook')
    status = db.Column(db.String(20), default='on_sale')
    seller_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        images_list = json.loads(self.images) if self.images else []
        
        condition_map = {
            'new': '全新',
            'like-new': '九成新',
            'good': '八成新',
            'fair': '七成新'
        }
        
        trade_method_map = {
            'face': '当面交易',
            'mail': '邮寄',
            'both': '皆可'
        }
        
        campus_map = {
            'zijingang': '紫金港校区',
            'yuquan': '玉泉校区',
            'xixi': '西溪校区',
            'zhijiang': '之江校区',
            'huajiachi': '华家池校区'
        }
        
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'edition': self.edition,
            'isbn': self.isbn,
            'condition': self.condition,
            'conditionLabel': condition_map.get(self.condition, '九成新'),
            'hasNotes': self.has_notes,
            'price': self.price,
            'originalPrice': self.original_price,
            'tradeMethod': self.trade_method,
            'tradeMethodLabel': trade_method_map.get(self.trade_method, '当面交易'),
            'campus': self.campus,
            'campusLabel': campus_map.get(self.campus, '紫金港校区'),
            'contact': self.contact,
            'images': images_list,
            'coverImage': images_list[0] if images_list else '/images/book1.jpg',
            'tags': self.tags,
            'description': self.description,
            'subject': self.subject,
            'grade': self.grade,
            'bookType': self.book_type,
            'status': self.status,
            'sellerId': self.seller_id,
            'seller': {
                'id': self.seller_id,
                'name': self.seller.name if self.seller else '未知用户',
                'reputation': self.seller.reputation if self.seller else 'A',
                'creditScore': self.seller.credit_score if self.seller else 100,
            },
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }