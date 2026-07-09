from datetime import datetime
from models import db


class KnowledgeMaterial(db.Model):
    __tablename__ = 'knowledge_materials'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    file_type = db.Column(db.String(50), default='other')
    file_size = db.Column(db.String(50))
    category = db.Column(db.String(100))
    course_name = db.Column(db.String(200))
    tags = db.Column(db.Text)
    price_points = db.Column(db.Integer, default=0)
    file_path = db.Column(db.String(500))
    cover_image = db.Column(db.String(500))
    download_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    uploader_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'title': self.title, 'description': self.description,
            'fileType': self.file_type, 'fileSize': self.file_size,
            'category': self.category, 'courseName': self.course_name,
            'tags': _split_tags(self.tags), 'pricePoints': self.price_points,
            'filePath': self.file_path, 'coverImage': self.cover_image,
            'downloadCount': self.download_count, 'viewCount': self.view_count,
            'likeCount': self.like_count, 'uploaderId': self.uploader_id,
            'status': self.status, 'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class KnowledgeDiscussion(db.Model):
    __tablename__ = 'knowledge_discussions'
    id = db.Column(db.Integer, primary_key=True)
    discussion_type = db.Column(db.String(50), default='讨论')
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.Text)
    author_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    like_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    last_reply_at = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'type': self.discussion_type, 'title': self.title,
            'content': self.content, 'tags': _split_tags(self.tags),
            'authorId': self.author_id, 'likeCount': self.like_count,
            'replyCount': self.reply_count, 'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


class KnowledgeComment(db.Model):
    __tablename__ = 'knowledge_comments'
    id = db.Column(db.Integer, primary_key=True)
    target_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('knowledge_comments.id'))
    author_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'targetType': self.target_type, 'targetId': self.target_id,
            'parentId': self.parent_id, 'authorId': self.author_id,
            'content': self.content, 'isDeleted': self.is_deleted,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class KnowledgeMaterialFavorite(db.Model):
    __tablename__ = 'knowledge_material_favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('knowledge_materials.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'userId': self.user_id, 'materialId': self.material_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class KnowledgeMaterialLike(db.Model):
    __tablename__ = 'knowledge_material_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('knowledge_materials.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class KnowledgeDiscussionLike(db.Model):
    __tablename__ = 'knowledge_discussion_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    discussion_id = db.Column(db.Integer, db.ForeignKey('knowledge_discussions.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class KnowledgeMaterialEntitlement(db.Model):
    __tablename__ = 'knowledge_material_entitlements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('knowledge_materials.id'), nullable=False)
    source = db.Column(db.String(50), default='download')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'userId': self.user_id, 'materialId': self.material_id,
            'source': self.source, 'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class KnowledgePointLedger(db.Model):
    __tablename__ = 'knowledge_point_ledger'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    delta = db.Column(db.Integer, nullable=False)
    balance_after = db.Column(db.Integer, nullable=False)
    reference_type = db.Column(db.String(50))
    reference_id = db.Column(db.Integer)
    note = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'userId': self.user_id, 'action': self.action,
            'delta': self.delta, 'balanceAfter': self.balance_after,
            'referenceType': self.reference_type, 'referenceId': self.reference_id,
            'note': self.note, 'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class KnowledgeCheckIn(db.Model):
    __tablename__ = 'knowledge_checkins'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    checkin_date = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'checkin_date'),)


class KnowledgeRank(db.Model):
    __tablename__ = 'knowledge_ranks'
    id = db.Column(db.Integer, primary_key=True)
    rank_type = db.Column(db.String(50), nullable=False)
    period = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id, 'rankType': self.rank_type, 'period': self.period,
            'userId': self.user_id, 'score': self.score,
        }


def _join_tags(tags):
    if not tags:
        return ''
    if isinstance(tags, str):
        return tags
    return ','.join(str(t) for t in tags)


def _split_tags(tags_str):
    if not tags_str:
        return []
    return [t.strip() for t in str(tags_str).split(',') if t.strip()]