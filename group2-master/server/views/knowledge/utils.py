from datetime import datetime

from flask import jsonify, request

from auth_utils import get_auth_error_response, get_request_user


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400, details=None):
    payload = {'code': code, 'message': message, 'data': None}
    if details is not None:
        payload['details'] = details
    return jsonify(payload), code


def require_user(optional=False):
    user = get_request_user(optional=optional)
    if not user:
        if optional:
            return None, None
        return None, get_auth_error_response()
    return user, None


def parse_page_args():
    page = max(1, request.args.get('page', 1, type=int))
    page_size = max(1, min(50, request.args.get('page_size', 20, type=int)))
    return page, page_size


def paginate_query(query, serializer):
    page, page_size = parse_page_args()
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {
        'items': [serializer(item) for item in items],
        'total': total,
        'page': page,
        'pageSize': page_size,
        'totalPages': (total + page_size - 1) // page_size,
    }


def today_key():
    return datetime.utcnow().strftime('%Y-%m-%d')
