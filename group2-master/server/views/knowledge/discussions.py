from datetime import datetime
from flask import request
from models import db, KnowledgeDiscussion, KnowledgeDiscussionLike, KnowledgeComment
from . import knowledge_bp
from .utils import success_response, error_response, require_user, paginate_query


@knowledge_bp.route('/api/knowledge/discussions', methods=['GET'])
def get_discussions():
    keyword = request.args.get('keyword', '').strip()
    dtype = request.args.get('type', '').strip()
    mine = request.args.get('mine', '').strip().lower() == 'true'
    user, _ = require_user() if mine else (None, None)
    user = user or require_user(optional=True)[0]

    query = KnowledgeDiscussion.query.filter_by(status='active')
    if mine and user:
        query = query.filter(KnowledgeDiscussion.author_id == user.id)
    if keyword:
        query = query.filter(db.or_(
            KnowledgeDiscussion.title.contains(keyword),
            KnowledgeDiscussion.content.contains(keyword),
        ))
    if dtype and dtype != '全部':
        query = query.filter(KnowledgeDiscussion.discussion_type == dtype)
    query = query.order_by(KnowledgeDiscussion.created_at.desc())
    return success_response(paginate_query(query, lambda i: i.to_dict()))


@knowledge_bp.route('/api/knowledge/discussions', methods=['POST'])
def create_discussion():
    user, err = require_user()
    if err:
        return err
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    if not title or not content:
        return error_response('标题和内容不能为空')

    from models.knowledge import _join_tags
    discussion = KnowledgeDiscussion(
        discussion_type=(data.get('type') or '讨论').strip(),
        title=title, content=content, tags=_join_tags(data.get('tags')),
        author_id=user.id, status='active',
        created_at=datetime.utcnow(), updated_at=datetime.utcnow(),
    )
    db.session.add(discussion)
    db.session.commit()
    return success_response(discussion.to_dict(), '讨论发布成功')


@knowledge_bp.route('/api/knowledge/discussions/<int:did>', methods=['DELETE'])
def delete_discussion(did):
    user, err = require_user()
    if err:
        return err
    discussion = db.session.get(KnowledgeDiscussion, did)
    if not discussion or discussion.status != 'active':
        return error_response('讨论不存在', 404)
    if discussion.author_id != user.id:
        return error_response('只能删除自己发布的讨论', 403)

    discussion.status = 'deleted'
    discussion.reply_count = 0
    discussion.updated_at = datetime.utcnow()
    KnowledgeComment.query.filter_by(target_type='discussion', target_id=did, is_deleted=False).update(
        {'is_deleted': True},
        synchronize_session=False,
    )
    db.session.commit()
    return success_response({'discussionId': did, 'status': discussion.status}, '讨论删除成功')


@knowledge_bp.route('/api/knowledge/discussions/<int:did>/like', methods=['POST'])
def toggle_discussion_like(did):
    user, err = require_user()
    if err:
        return err
    discussion = db.session.get(KnowledgeDiscussion, did)
    if not discussion or discussion.status != 'active':
        return error_response('讨论不存在', 404)
    record = KnowledgeDiscussionLike.query.filter_by(user_id=user.id, discussion_id=did).first()
    if record:
        db.session.delete(record)
        discussion.like_count = max(0, (discussion.like_count or 0) - 1)
        db.session.commit()
        return success_response({'liked': False, 'discussionId': did, 'likeCount': discussion.like_count}, '已取消点赞')
    db.session.add(KnowledgeDiscussionLike(user_id=user.id, discussion_id=did))
    discussion.like_count = (discussion.like_count or 0) + 1
    db.session.commit()
    return success_response({'liked': True, 'discussionId': did, 'likeCount': discussion.like_count}, '点赞成功')


@knowledge_bp.route('/api/knowledge/comments', methods=['POST'])
def create_comment():
    user, err = require_user()
    if err:
        return err
    data = request.get_json() or {}
    target_type = data.get('targetType', '').strip()
    target_id = int(data.get('targetId', 0) or 0)
    content = data.get('content', '').strip()

    if target_type not in {'material', 'discussion'} or target_id <= 0 or not content:
        return error_response('参数无效')

    comment = KnowledgeComment(target_type=target_type, target_id=target_id,
                               parent_id=data.get('parentId'), author_id=user.id, content=content)
    db.session.add(comment)

    if target_type == 'discussion':
        discussion = db.session.get(KnowledgeDiscussion, target_id)
        if discussion:
            discussion.reply_count = (discussion.reply_count or 0) + 1
            discussion.last_reply_at = datetime.utcnow()
            discussion.updated_at = datetime.utcnow()

    db.session.commit()
    return success_response(comment.to_dict(), '评论发布成功')


@knowledge_bp.route('/api/knowledge/comments/<int:cid>', methods=['DELETE'])
def delete_comment(cid):
    user, err = require_user()
    if err:
        return err
    comment = db.session.get(KnowledgeComment, cid)
    if not comment:
        return error_response('评论不存在', 404)
    if comment.author_id != user.id:
        return error_response('只能删除自己的评论', 403)
    if comment.is_deleted:
        return success_response(comment.to_dict(), '评论已删除')

    comment.is_deleted = True
    db.session.commit()
    return success_response(comment.to_dict(), '评论删除成功')
