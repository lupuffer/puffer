import json
from datetime import datetime

from flask import Blueprint, request

from models import db
from models.book import Book
from models.user import User
from system_notifications import notify_shortage_matches
from .books_helpers import error_response, require_user, success_response

books_bp = Blueprint('books', __name__)


@books_bp.route('/api/books', methods=['GET'])
def get_books():
    keyword = request.args.get('keyword', '').strip()
    subject = request.args.get('subject', '').strip()
    grade = request.args.get('grade', '').strip()
    condition = request.args.get('condition', '').strip()
    book_type = request.args.get('type', '').strip()
    campus = request.args.get('campus', '').strip()
    trade_method = request.args.get('trade_method', '').strip()
    has_notes = request.args.get('has_notes', '').strip().lower()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)

    query = Book.query.filter_by(status='on_sale')

    if keyword:
        query = query.filter(db.or_(
            Book.title.contains(keyword), Book.author.contains(keyword),
            Book.isbn.contains(keyword), Book.tags.contains(keyword),
        ))

    if subject and subject != '全部':
        query = query.filter(Book.subject == subject)
    if grade and grade != '全部':
        query = query.filter(Book.grade == grade)
    if condition and condition != '全部':
        query = query.filter(Book.condition == condition)
    if book_type and book_type != '全部':
        query = query.filter(Book.book_type == book_type)
    if campus and campus != '全部':
        query = query.filter(Book.campus == campus)
    if trade_method and trade_method != '全部':
        query = query.filter(Book.trade_method == trade_method)
    if has_notes in ('true', 'false'):
        query = query.filter(Book.has_notes.is_(has_notes == 'true'))

    if min_price is not None:
        query = query.filter(Book.price >= min_price)
    if max_price is not None:
        query = query.filter(Book.price <= max_price)

    if sort_by == 'price_asc':
        query = query.order_by(Book.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Book.price.desc())
    elif sort_by == 'reputation':
        query = query.join(Book.seller).order_by(User.credit_score.desc(), Book.created_at.desc())
    else:
        query = query.order_by(Book.created_at.desc())

    total = query.count()
    books = query.offset((page - 1) * page_size).limit(page_size).all()

    return success_response({
        'books': [book.to_dict() for book in books], 'total': total,
        'page': page, 'page_size': page_size, 'total_pages': (total + page_size - 1) // page_size,
    })


@books_bp.route('/api/books/<int:book_id>', methods=['GET'])
def get_book_detail(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        return error_response('书籍不存在', 404)
    if book.status == 'draft':
        return error_response('书籍不存在', 404)
    return success_response(book.to_dict())


@books_bp.route('/api/books', methods=['POST'])
def create_book():
    user, err_response = require_user()
    if err_response:
        return err_response

    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return error_response('书名不能为空')

    price = data.get('price')
    if price is None or float(price) <= 0:
        return error_response('价格必须大于 0')

    images = data.get('images', [])
    if isinstance(images, str):
        images = [images]
    if data.get('image') and data['image'] not in images:
        images.insert(0, data['image'])

    book = Book(
        title=title, author=data.get('author', '').strip(),
        publisher=data.get('publisher', '').strip(), edition=data.get('edition', '').strip(),
        isbn=data.get('isbn', '').strip(), condition=data.get('condition', 'like-new'),
        has_notes=data.get('hasNotes', False), price=float(price),
        original_price=float(data['originalPrice']) if data.get('originalPrice') else None,
        trade_method=data.get('tradeMethod', 'face'), campus=data.get('campus', 'zijingang'),
        contact=data.get('contact', '').strip(), images=json.dumps(images),
        tags=data.get('tags', ''), description=data.get('description', '').strip(),
        subject=data.get('subject', ''), grade=data.get('grade', ''),
        book_type=data.get('bookType', 'textbook'), seller_id=user.id, status='on_sale',
    )

    db.session.add(book)
    db.session.commit()

    try:
        notify_shortage_matches(book)
    except Exception as exc:
        db.session.rollback()
        print(f'shortage notification failed for book {book.id}: {exc}')

    return success_response(book.to_dict(), '书籍发布成功')


@books_bp.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    user, err_response = require_user()
    if err_response:
        return err_response

    book = db.session.get(Book, book_id)
    if not book:
        return error_response('书籍不存在', 404)
    if book.seller_id != user.id:
        return error_response('无权修改此书', 403)

    data = request.get_json() or {}
    for field in ['title', 'author', 'publisher', 'edition', 'isbn', 'condition', 'price',
                  'originalPrice', 'tradeMethod', 'campus', 'contact', 'tags',
                  'description', 'subject', 'grade', 'bookType', 'hasNotes', 'images']:
        if field not in data:
            continue
        if field == 'price':
            book.price = float(data[field])
        elif field == 'originalPrice':
            book.original_price = float(data[field]) if data[field] else None
        elif field == 'hasNotes':
            book.has_notes = bool(data[field])
        elif field == 'images':
            book.images = json.dumps(data[field] or [])
        elif field == 'tradeMethod':
            book.trade_method = data[field]
        elif field == 'bookType':
            book.book_type = data[field]
        else:
            setattr(book, field, data[field])

    book.updated_at = datetime.utcnow()
    db.session.commit()
    return success_response(book.to_dict(), '书籍更新成功')


@books_bp.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    user, err_response = require_user()
    if err_response:
        return err_response

    book = db.session.get(Book, book_id)
    if not book:
        return error_response('书籍不存在', 404)
    if book.seller_id != user.id:
        return error_response('无权删除此书', 403)

    book.status = 'removed'
    db.session.commit()
    return success_response(None, '书籍已下架')


@books_bp.route('/api/books/my', methods=['GET'])
def get_my_books():
    user, err_response = require_user()
    if err_response:
        return err_response

    books = Book.query.filter(
        Book.seller_id == user.id,
        Book.status != 'draft',
    ).order_by(Book.created_at.desc()).all()
    return success_response([book.to_dict() for book in books])
