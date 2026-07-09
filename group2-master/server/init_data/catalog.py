import json
import math
from datetime import datetime
from pathlib import Path

from models import Book, db

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR.parent / 'client' / 'public' / 'data' / 'data.json'
CATALOG_COUNT = 100000
BOOK_BATCH_SIZE = 2000

SELLER_IDS = ['seller_001', 'seller_002', 'seller_003', 'seller_004', 'seller_005']
CAMPUSES = ['zijingang', 'yuquan', 'xixi', 'zhijiang', 'huajiachi']
CONDITIONS = ['new', 'like-new', 'good', 'fair']
AUTHOR_CYCLE = [f'作者{i}' for i in range(1, 11)]


def truncate_one_decimal(value):
    numeric = float(value or 0)
    return math.floor(numeric * 10) / 10


def catalog_author(item_id):
    return AUTHOR_CYCLE[(item_id - 1) % len(AUTHOR_CYCLE)]


def load_frontend_catalog():
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f'catalog not found: {CATALOG_PATH}')
    with CATALOG_PATH.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list) or len(data) < CATALOG_COUNT:
        raise ValueError(f'catalog invalid, expected {CATALOG_COUNT}+ rows')
    return data


def map_catalog_item(item):
    item_id = int(item['id'])
    price = truncate_one_decimal(item.get('price', 0) or 0)
    image = str(item.get('img', '/images/book1.jpg')).replace('./images/', '/images/')
    condition = CONDITIONS[item_id % len(CONDITIONS)]
    campus = CAMPUSES[item_id % len(CAMPUSES)]
    created = datetime(2024, 1, 1, 0, 0, 0)
    return {
        'id': item_id, 'title': str(item.get('name') or f'Book {item_id}'),
        'author': catalog_author(item_id), 'publisher': 'SeekBook Catalog',
        'edition': 'Catalog Edition', 'isbn': f'9787{item_id:09d}'[-13:],
        'condition': condition, 'has_notes': bool(item_id % 7 == 0),
        'price': price, 'original_price': truncate_one_decimal(price * 1.15),
        'trade_method': 'face', 'campus': campus,
        'contact': 'catalog@seekbook.local', 'images': json.dumps([image]),
        'tags': 'catalog,migrated,frontend', 'description': f'Frontend migrated item {item_id}',
        'subject': 'general', 'grade': 'general', 'book_type': 'textbook',
        'status': 'on_sale', 'seller_id': SELLER_IDS[item_id % len(SELLER_IDS)],
        'created_at': created, 'updated_at': created,
    }


def catalog_is_synced(source_items):
    existing = Book.query.filter(Book.id <= CATALOG_COUNT).count()
    if existing != len(source_items):
        return False

    sample_ids = [1, len(source_items) // 2, len(source_items)]
    sample_rows = {
        row.id: {'title': row.title, 'author': row.author, 'price': float(row.price or 0)}
        for row in Book.query.filter(Book.id.in_(sample_ids)).all()
    }
    for sid in sample_ids:
        source_item = source_items[sid - 1]
        expected_title = str(source_item.get('name') or f'Book {sid}')
        expected_author = catalog_author(sid)
        expected_price = truncate_one_decimal(source_item.get('price', 0) or 0)
        sample = sample_rows.get(sid)
        if not sample:
            return False
        if sample.get('title') != expected_title or sample.get('author') != expected_author:
            return False
        if abs(sample.get('price', 0) - expected_price) > 1e-9:
            return False
    return True


def sync_catalog_books():
    source_items = load_frontend_catalog()
    if catalog_is_synced(source_items):
        print(f'catalog already synced: {len(source_items)} rows')
        return

    print(f'syncing catalog: {len(source_items)} rows')
    Book.query.filter(Book.id <= CATALOG_COUNT).delete(synchronize_session=False)
    db.session.commit()

    for start in range(0, len(source_items), BOOK_BATCH_SIZE):
        batch = source_items[start:start + BOOK_BATCH_SIZE]
        db.session.bulk_insert_mappings(Book, [map_catalog_item(i) for i in batch])
        db.session.commit()
        print(f'  synced {start + len(batch)}/{len(source_items)}')
