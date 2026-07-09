from datetime import datetime
from flask import request
from models import db, KnowledgeMaterial, KnowledgeMaterialEntitlement, KnowledgeMaterialFavorite, KnowledgeMaterialLike
from . import knowledge_bp
from .utils import success_response, error_response, require_user, paginate_query
from .points import _get_points_balance, award_points, deduct_points, points_payload

UPLOAD_REWARD = 10


@knowledge_bp.route('/api/knowledge/materials', methods=['GET'])
def get_materials():
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    mine = request.args.get('mine', '').strip().lower() == 'true'
    user, _ = require_user() if mine else (None, None)
    user = user or require_user(optional=True)[0]

    query = KnowledgeMaterial.query.filter_by(status='active')
    if mine and user:
        query = query.filter(KnowledgeMaterial.uploader_id == user.id)
    if keyword:
        query = query.filter(db.or_(
            KnowledgeMaterial.title.contains(keyword),
            KnowledgeMaterial.description.contains(keyword),
            KnowledgeMaterial.tags.contains(keyword),
        ))
    if category and category != '全部':
        query = query.filter(KnowledgeMaterial.category == category)
    query = query.order_by(KnowledgeMaterial.created_at.desc())
    return success_response(paginate_query(query, lambda i: i.to_dict()))


@knowledge_bp.route('/api/knowledge/materials', methods=['POST'])
def create_material():
    user, err = require_user()
    if err:
        return err
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    if not title:
        return error_response('资料标题不能为空')

    description = data.get('description', '').strip()
    if not description:
        return error_response('资料描述不能为空', 400)

    from models.knowledge import _join_tags
    material = KnowledgeMaterial(
        title=title, description=description,
        file_type=data.get('fileType', '').strip() or 'other',
        file_size=str(data.get('fileSize', '') or ''),
        category=data.get('category', '').strip(),
        course_name=(data.get('courseName') or data.get('course', '')).strip(),
        tags=_join_tags(data.get('tags')), price_points=max(0, int(data.get('pricePoints', 0) or 0)),
        file_path=data.get('filePath', '').strip(), cover_image=data.get('coverImage', '').strip(),
        uploader_id=user.id, status='active', created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
    )
    db.session.add(material)
    reward = award_points(user, UPLOAD_REWARD, 'upload_material', 'material', None, '上传资料奖励')
    db.session.flush()
    if reward.get('entry'):
        reward['entry'].reference_id = material.id
    db.session.commit()
    return success_response({'material': material.to_dict(), 'points': points_payload(user)}, '资料上传成功')


@knowledge_bp.route('/api/knowledge/materials/<int:mid>/download', methods=['POST'])
def download_material(mid):
    user, err = require_user()
    if err:
        return err
    material = db.session.get(KnowledgeMaterial, mid)
    if not material or material.status != 'active':
        return error_response('资料不存在', 404)

    record = KnowledgeMaterialEntitlement.query.filter_by(user_id=user.id, material_id=mid).first()
    points_change = None
    if not record:
        if (material.price_points or 0) > 0:
            points_change = deduct_points(user, material.price_points, 'download_material', 'material', mid, f'下载资料 {material.title}')
            if not points_change:
                balance = _get_points_balance(user)
                price_points = int(material.price_points or 0)
                shortfall = max(0, price_points - balance)
                return error_response(
                    f'积分不足，还差 {shortfall} 分',
                    400,
                    {
                        'code': 'INSUFFICIENT_POINTS',
                        'balance': balance,
                        'pricePoints': price_points,
                        'shortfall': shortfall,
                    },
                )
        record = KnowledgeMaterialEntitlement(user_id=user.id, material_id=mid, source='download')
        db.session.add(record)

    material.download_count = (material.download_count or 0) + 1
    material.updated_at = datetime.utcnow()
    db.session.commit()
    return success_response({'material': material.to_dict(), 'entitlement': record.to_dict(), 'points': points_payload(user)}, '下载权益已记录')


@knowledge_bp.route('/api/knowledge/materials/<int:mid>', methods=['DELETE'])
def delete_material(mid):
    user, err = require_user()
    if err:
        return err
    material = db.session.get(KnowledgeMaterial, mid)
    if not material or material.status != 'active':
        return error_response('资料不存在', 404)
    if material.uploader_id != user.id:
        return error_response('只能删除自己上传的资料', 403)

    material.status = 'deleted'
    material.updated_at = datetime.utcnow()
    db.session.commit()
    return success_response({'materialId': mid, 'status': material.status}, '资料删除成功')


@knowledge_bp.route('/api/knowledge/materials/<int:mid>/favorite', methods=['POST'])
def toggle_favorite(mid):
    user, err = require_user()
    if err:
        return err
    material = db.session.get(KnowledgeMaterial, mid)
    if not material or material.status != 'active':
        return error_response('资料不存在', 404)
    record = KnowledgeMaterialFavorite.query.filter_by(user_id=user.id, material_id=mid).first()
    if record:
        db.session.delete(record)
        db.session.commit()
        return success_response({'favorited': False, 'materialId': mid}, '已取消收藏')
    db.session.add(KnowledgeMaterialFavorite(user_id=user.id, material_id=mid))
    db.session.commit()
    return success_response({'favorited': True, 'materialId': mid}, '收藏成功')


@knowledge_bp.route('/api/knowledge/materials/<int:mid>/like', methods=['POST'])
def toggle_like(mid):
    user, err = require_user()
    if err:
        return err
    material = db.session.get(KnowledgeMaterial, mid)
    if not material or material.status != 'active':
        return error_response('资料不存在', 404)
    record = KnowledgeMaterialLike.query.filter_by(user_id=user.id, material_id=mid).first()
    if record:
        db.session.delete(record)
        material.like_count = max(0, (material.like_count or 0) - 1)
        db.session.commit()
        return success_response({'liked': False, 'materialId': mid, 'likeCount': material.like_count}, '已取消点赞')
    db.session.add(KnowledgeMaterialLike(user_id=user.id, material_id=mid))
    material.like_count = (material.like_count or 0) + 1
    db.session.commit()
    return success_response({'liked': True, 'materialId': mid, 'likeCount': material.like_count}, '点赞成功')
