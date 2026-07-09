from datetime import datetime
from . import db

class Favorite(db.Model):
    """收藏表"""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id', name='unique_user_book_favorite'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'bookId': self.book_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }