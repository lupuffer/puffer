from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .book import Book
from .order import Order
from .chat import ChatSession, Message
from .favorite import Favorite
from .note import Note
from .revoked_token import RevokedToken
from .shortage_registration import ShortageRegistration
from .credit_audit import CreditAudit
from .knowledge import (
    KnowledgeCheckIn,
    KnowledgeComment,
    KnowledgeDiscussion,
    KnowledgeDiscussionLike,
    KnowledgeMaterial,
    KnowledgeMaterialEntitlement,
    KnowledgeMaterialFavorite,
    KnowledgeMaterialLike,
    KnowledgePointLedger,
    KnowledgeRank,
)

__all__ = [
    'db', 'User', 'Book', 'Order', 'ChatSession', 'Message',
    'Favorite', 'Note', 'RevokedToken', 'ShortageRegistration', 'CreditAudit',
    'KnowledgeMaterial', 'KnowledgeDiscussion', 'KnowledgeComment',
    'KnowledgeMaterialFavorite', 'KnowledgeMaterialEntitlement',
    'KnowledgeMaterialLike', 'KnowledgeDiscussionLike',
    'KnowledgePointLedger', 'KnowledgeCheckIn', 'KnowledgeRank'
]
