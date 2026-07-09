from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash
from models import db

DEFAULT_PASSWORD = '123456'


def ensure_runtime_schema():
    inspector = inspect(db.engine)

    user_cols = {c['name'] for c in inspector.get_columns('users')}
    if 'username' not in user_cols:
        db.session.execute(text('ALTER TABLE users ADD COLUMN username VARCHAR(100)'))
    if 'email' not in user_cols:
        db.session.execute(text('ALTER TABLE users ADD COLUMN email VARCHAR(255)'))
    if 'password_hash' not in user_cols:
        db.session.execute(text('ALTER TABLE users ADD COLUMN password_hash VARCHAR(255)'))
    if 'points_balance' not in user_cols:
        db.session.execute(text('ALTER TABLE users ADD COLUMN points_balance INTEGER DEFAULT 0'))
    if 'college' not in user_cols:
        db.session.execute(text('ALTER TABLE users ADD COLUMN college VARCHAR(100)'))
    if 'grade' not in user_cols:
        db.session.execute(text('ALTER TABLE users ADD COLUMN grade VARCHAR(50)'))
    if 'campus' not in user_cols:
        db.session.execute(text('ALTER TABLE users ADD COLUMN campus VARCHAR(100)'))
    if 'phone' not in user_cols:
        db.session.execute(text('ALTER TABLE users ADD COLUMN phone VARCHAR(30)'))

    order_cols = {c['name'] for c in inspector.get_columns('orders')}
    if 'meet_time' not in order_cols:
        db.session.execute(text('ALTER TABLE orders ADD COLUMN meet_time VARCHAR(100)'))
    if 'meet_place' not in order_cols:
        db.session.execute(text('ALTER TABLE orders ADD COLUMN meet_place VARCHAR(200)'))
    if 'confirmed_at' not in order_cols:
        db.session.execute(text('ALTER TABLE orders ADD COLUMN confirmed_at DATETIME'))
    if 'buyer_completed_confirmed' not in order_cols:
        db.session.execute(text('ALTER TABLE orders ADD COLUMN buyer_completed_confirmed BOOLEAN DEFAULT 0'))
    if 'seller_completed_confirmed' not in order_cols:
        db.session.execute(text('ALTER TABLE orders ADD COLUMN seller_completed_confirmed BOOLEAN DEFAULT 0'))
    if 'cancelled_at' not in order_cols:
        db.session.execute(text('ALTER TABLE orders ADD COLUMN cancelled_at DATETIME'))
    if 'cancelled_by' not in order_cols:
        db.session.execute(text('ALTER TABLE orders ADD COLUMN cancelled_by VARCHAR(50)'))
    if 'cancelled_from_status' not in order_cols:
        db.session.execute(text('ALTER TABLE orders ADD COLUMN cancelled_from_status VARCHAR(20)'))

    audit_tables = set(inspector.get_table_names())
    if 'credit_audits' in audit_tables:
        audit_cols = {c['name'] for c in inspector.get_columns('credit_audits')}
        if 'behavior_score' not in audit_cols:
            db.session.execute(text('ALTER TABLE credit_audits ADD COLUMN behavior_score FLOAT'))
            if 'completion_score' in audit_cols:
                db.session.execute(text('UPDATE credit_audits SET behavior_score = completion_score WHERE behavior_score IS NULL'))

    chat_cols = {c['name'] for c in inspector.get_columns('chat_sessions')}
    if 'buyer_unread_count' not in chat_cols:
        db.session.execute(text('ALTER TABLE chat_sessions ADD COLUMN buyer_unread_count INTEGER DEFAULT 0'))
    if 'seller_unread_count' not in chat_cols:
        db.session.execute(text('ALTER TABLE chat_sessions ADD COLUMN seller_unread_count INTEGER DEFAULT 0'))
    if 'is_system_session' not in chat_cols:
        db.session.execute(text('ALTER TABLE chat_sessions ADD COLUMN is_system_session BOOLEAN DEFAULT 0'))

    mat_cols = {c['name'] for c in inspector.get_columns('knowledge_materials')}
    if 'tags' not in mat_cols:
        db.session.execute(text('ALTER TABLE knowledge_materials ADD COLUMN tags TEXT'))
    if 'price_points' not in mat_cols:
        db.session.execute(text('ALTER TABLE knowledge_materials ADD COLUMN price_points INTEGER DEFAULT 0'))

    db.session.commit()

    pwd_hash = generate_password_hash(DEFAULT_PASSWORD)
    db.session.execute(text("UPDATE users SET username = id WHERE username IS NULL OR username = ''"))
    db.session.execute(text("UPDATE users SET email = LOWER(COALESCE(username, id)) || '@seekbook.local' WHERE email IS NULL OR email = ''"))
    db.session.execute(text("UPDATE users SET password_hash = :pwd WHERE password_hash IS NULL OR password_hash = ''"), {'pwd': pwd_hash})
    db.session.execute(text("UPDATE users SET points_balance = 0 WHERE points_balance IS NULL"))
    db.session.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email_unique ON users (email)'))
    db.session.execute(text("UPDATE orders SET buyer_completed_confirmed = 1, seller_completed_confirmed = 1 WHERE status = 'completed'"))
    db.session.commit()
