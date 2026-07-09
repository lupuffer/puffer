from .catalog import sync_catalog_books
from .schema import ensure_runtime_schema
from .seeds import seed_users, seed_notes, seed_knowledge_data
from .schedule_books import seed_schedule_books
from system_notifications import ensure_system_user


def init_database(app):
    """鍒濆鍖栨暟鎹簱"""
    with app.app_context():
        from models import db, User, Book, Note, KnowledgeMaterial
        db.create_all()
        ensure_runtime_schema()

        if User.query.count() == 0:
            print('棣栨鍒濆鍖栵細鍒涘缓娴嬭瘯鐢ㄦ埛鍜屽熀纭€鏁版嵁...')
            seed_users()
            sync_catalog_books()
            seed_notes()
            seed_knowledge_data()
        else:
            sync_catalog_books()

        seed_schedule_books()
        ensure_system_user()

        from models import CreditAudit
        from views.credit_utils import recalc_credit_for_user
        users_without_credit_audit = (
            User.query
            .filter(User.role != 'system')
            .filter(~User.id.in_(db.session.query(CreditAudit.user_id)))
            .all()
        )
        for user in users_without_credit_audit:
            recalc_credit_for_user(
                user,
                trigger_type='credit_model_baseline',
                trigger_ref='v2',
            )
        if users_without_credit_audit:
            db.session.commit()

        print(f'db ready: users={User.query.count()}, books={Book.query.count()}, '
              f'notes={Note.query.count()}, materials={KnowledgeMaterial.query.count()}')
