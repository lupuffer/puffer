from flask import Blueprint, jsonify, request

from auth_utils import get_auth_error_response, get_request_user
from models import Book, KnowledgeComment, Note, db

notes_bp = Blueprint('notes', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), code


def parse_tags(tags):
    if tags is None:
        return ''
    if isinstance(tags, str):
        return ','.join([tag.strip() for tag in tags.split(',') if tag.strip()])
    if isinstance(tags, list):
        return ','.join([str(tag).strip() for tag in tags if str(tag).strip()])
    return str(tags).strip()


def require_user():
    user = get_request_user()
    if not user:
        return None, get_auth_error_response()
    return user, None


@notes_bp.route('/api/notes', methods=['GET'])
def get_notes():
    book_id = request.args.get('bookId', type=int)
    query = Note.query.filter_by(status='active')
    if book_id:
        query = query.filter_by(book_id=book_id)

    notes = query.order_by(Note.created_at.desc()).all()
    return success_response({'notes': [note.to_dict() for note in notes]})


@notes_bp.route('/api/notes', methods=['POST'])
def create_note():
    user, error = require_user()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    tags = parse_tags(data.get('tags'))
    book_id = data.get('bookId')

    if not title:
        return error_response('标题不能为空', 400)
    if not content:
        return error_response('内容不能为空', 400)

    if book_id is not None:
        try:
            book_id = int(book_id)
        except (TypeError, ValueError):
            return error_response('bookId 必须为整数', 400)
        book = db.session.get(Book, book_id)
        if not book:
            return error_response('关联书籍不存在', 404)
    else:
        book = None
        book_id = None

    note = Note(
        title=title,
        content=content,
        author_id=user.id,
        book_id=book_id,
        tags=tags,
        status='active',
    )

    db.session.add(note)
    db.session.commit()
    return success_response(note.to_dict(), '笔记发布成功')


@notes_bp.route('/api/community/notes', methods=['GET'])
def get_community_notes():
    query = Note.query.filter_by(status='active')
    notes = query.order_by(Note.created_at.desc()).limit(50).all()
    return success_response({'notes': [note.to_dict() for note in notes]})


@notes_bp.route('/api/community/notes', methods=['POST'])
def create_community_note():
    user, error = require_user()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    tags = parse_tags(data.get('tags'))
    related_book_id = data.get('related_book_id') or data.get('bookId') or data.get('book_id')

    if not title:
        return error_response('标题不能为空', 400)
    if not content:
        return error_response('内容不能为空', 400)

    if related_book_id is not None:
        try:
            related_book_id = int(related_book_id)
        except (TypeError, ValueError):
            return error_response('关联书籍ID无效', 400)
        book = db.session.get(Book, related_book_id)
        if not book:
            return error_response('关联书籍不存在', 404)
    else:
        related_book_id = None

    note = Note(
        title=title,
        content=content,
        author_id=user.id,
        book_id=related_book_id,
        tags=tags,
        status='active',
    )

    db.session.add(note)
    db.session.commit()
    return success_response(note.to_dict(), '笔记发布成功')


@notes_bp.route('/api/notes/<int:note_id>/comments', methods=['GET'])
def get_note_comments(note_id):
    note = db.session.get(Note, note_id)
    if not note or note.status != 'active':
        return error_response('笔记不存在', 404)

    comments = KnowledgeComment.query.filter_by(
        target_type='note',
        target_id=note_id,
        is_deleted=False
    ).order_by(KnowledgeComment.created_at.asc()).all()

    return success_response({'comments': [comment.to_dict() for comment in comments]})


@notes_bp.route('/api/notes/comment', methods=['POST'])
def create_note_comment():
    user, error = require_user()
    if error:
        return error

    data = request.get_json(silent=True) or {}
    note_id = data.get('note_id')
    comment_text = (data.get('comment_text') or '').strip()

    if note_id is None:
        return error_response('note_id不能为空', 400)
    if not comment_text:
        return error_response('评论内容不能为空', 400)

    try:
        note_id = int(note_id)
    except (TypeError, ValueError):
        return error_response('note_id必须为整数', 400)

    note = db.session.get(Note, note_id)
    if not note or note.status != 'active':
        return error_response('笔记不存在', 404)

    comment = KnowledgeComment(
        target_type='note',
        target_id=note_id,
        parent_id=None,
        author_id=user.id,
        content=comment_text,
    )

    db.session.add(comment)
    db.session.commit()

    comments = KnowledgeComment.query.filter_by(
        target_type='note',
        target_id=note_id,
        is_deleted=False
    ).order_by(KnowledgeComment.created_at.asc()).all()

    return success_response({'comments': [c.to_dict() for c in comments]}, '评论发布成功')
