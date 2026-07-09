from datetime import datetime
from . import db

class Note(db.Model):
    """社区笔记表"""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=True)
    likes = db.Column(db.Integer, default=0)
    views = db.Column(db.Integer, default=0)
    tags = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    book = db.relationship('Book', backref='book_notes')
    author = db.relationship('User', foreign_keys=[author_id], backref='authored_notes')

    def to_dict(self):
        from models import User
        author = User.query.get(self.author_id)
        return {
            'id': self.id,
            'note_id': self.id,
            'title': self.title,
            'content': self.content,
            'author': {
                'id': self.author_id,
                'name': author.name if author else '未知用户'
            },
            'book': self.book.to_dict() if self.book else None,
            'likes': self.likes,
            'views': self.views,
            'tags': self.tags.split(',') if self.tags else [],
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
