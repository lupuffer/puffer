from datetime import datetime

from . import db

STATUS_LABELS = {
    'waiting': '等待中',
    'matched': '已匹配',
}

CAMPUS_LABELS = {
    'zijingang': '紫金港校区',
    'yuquan': '玉泉校区',
    'xixi': '西溪校区',
    'zhijiang': '之江校区',
    'huajiachi': '华家池校区',
}


class ShortageRegistration(db.Model):
    __tablename__ = 'shortage_registrations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(50), db.ForeignKey('users.id'), nullable=False, index=True)
    book_name = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(20), nullable=True)
    campus = db.Column(db.String(100), nullable=True)
    expected_price = db.Column(db.Float, nullable=True)
    note = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='waiting')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'bookName': self.book_name,
            'isbn': self.isbn,
            'campus': self.campus,
            'campusLabel': CAMPUS_LABELS.get(self.campus, self.campus or ''),
            'expectedPrice': self.expected_price,
            'note': self.note,
            'status': self.status,
            'statusLabel': STATUS_LABELS.get(self.status, '等待中'),
            'summaryLine': self.build_summary_line(),
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

    def build_summary_line(self):
        parts = []
        campus_label = CAMPUS_LABELS.get(self.campus, self.campus or '')
        if campus_label:
            parts.append(campus_label)
        if isinstance(self.expected_price, (int, float)) and self.expected_price > 0:
            parts.append(f'期望不高于 ¥{self.expected_price:.2f}')
        if parts:
            return ' / '.join(parts)
        if self.isbn:
            return f'ISBN: {self.isbn}'
        return '已登记，等待同学上架'
