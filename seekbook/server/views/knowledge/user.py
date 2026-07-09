from flask import request
from models import db, KnowledgeMaterial, KnowledgeDiscussion, KnowledgeComment, KnowledgeMaterialFavorite, KnowledgeMaterialEntitlement, KnowledgeRank
from . import knowledge_bp
from .utils import success_response, require_user, paginate_query
from .points import _get_points_balance, points_payload, today_key


@knowledge_bp.route('/api/knowledge/ranks', methods=['GET'])
def get_ranks():
    rank_type = request.args.get('rank_type', '').strip()
    period = request.args.get('period', '').strip() or 'month'
    query = KnowledgeRank.query.filter_by(period=period)
    if rank_type:
        query = query.filter(KnowledgeRank.rank_type == rank_type)
    ranks = query.order_by(KnowledgeRank.score.desc(), KnowledgeRank.id.asc()).all()
    return success_response([r.to_dict() for r in ranks])


@knowledge_bp.route('/api/knowledge/me/overview', methods=['GET'])
def get_overview():
    user, err = require_user()
    if err:
        return err

    uploads = KnowledgeMaterial.query.filter_by(uploader_id=user.id, status='active').count()
    discussions = KnowledgeDiscussion.query.filter_by(author_id=user.id, status='active').count()
    comments = KnowledgeComment.query.filter_by(author_id=user.id, is_deleted=False).count()
    favorites = KnowledgeMaterialFavorite.query.filter_by(user_id=user.id).count()
    redeems = KnowledgeMaterialEntitlement.query.filter_by(user_id=user.id).count()

    mat_likes = db.session.query(db.func.coalesce(db.func.sum(KnowledgeMaterial.like_count), 0)).filter(
        KnowledgeMaterial.uploader_id == user.id, KnowledgeMaterial.status == 'active'
    ).scalar()
    disc_likes = db.session.query(db.func.coalesce(db.func.sum(KnowledgeDiscussion.like_count), 0)).filter(
        KnowledgeDiscussion.author_id == user.id, KnowledgeDiscussion.status == 'active'
    ).scalar()

    return success_response({
        'uploads': uploads, 'discussions': discussions, 'comments': comments,
        'favorites': favorites, 'redeems': redeems,
        'likes': int(mat_likes or 0) + int(disc_likes or 0),
        'pointsBalance': _get_points_balance(user),
        'checkedInToday': KnowledgeCheckIn.query.filter_by(user_id=user.id, checkin_date=today_key()).first() is not None,
    })


from models import KnowledgeCheckIn


@knowledge_bp.route('/api/knowledge/me/uploads', methods=['GET'])
def get_uploads():
    user, err = require_user()
    if err:
        return err
    query = KnowledgeMaterial.query.filter_by(uploader_id=user.id, status='active').order_by(KnowledgeMaterial.created_at.desc())
    return success_response(paginate_query(query, lambda i: i.to_dict()))


@knowledge_bp.route('/api/knowledge/me/discussions', methods=['GET'])
def get_my_discussions():
    user, err = require_user()
    if err:
        return err
    query = KnowledgeDiscussion.query.filter_by(author_id=user.id, status='active').order_by(KnowledgeDiscussion.created_at.desc())
    return success_response(paginate_query(query, lambda i: i.to_dict()))


@knowledge_bp.route('/api/knowledge/me/favorites', methods=['GET'])
def get_favorites():
    user, err = require_user()
    if err:
        return err
    query = KnowledgeMaterialFavorite.query.filter_by(user_id=user.id).order_by(KnowledgeMaterialFavorite.created_at.desc())
    return success_response(paginate_query(query, serialize_material_record))


@knowledge_bp.route('/api/knowledge/me/redeems', methods=['GET'])
def get_redeems():
    user, err = require_user()
    if err:
        return err
    query = KnowledgeMaterialEntitlement.query.filter_by(user_id=user.id).order_by(KnowledgeMaterialEntitlement.created_at.desc())
    return success_response(paginate_query(query, serialize_material_record))


def serialize_material_record(record):
    payload = record.to_dict()
    material = db.session.get(KnowledgeMaterial, record.material_id)
    payload['material'] = material.to_dict() if material and material.status == 'active' else None
    return payload
