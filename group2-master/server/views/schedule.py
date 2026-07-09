import io
import json
import math
import uuid
from flask import Blueprint, jsonify, request
from auth_utils import get_auth_error_response, get_request_user
from models import Book

schedule_bp = Blueprint('schedule', __name__)


def success_response(data=None, message='success'):
    return jsonify({'code': 200, 'message': message, 'data': data})


def error_response(message='error', code=400):
    return jsonify({'code': code, 'message': message, 'data': None}), code


def require_user():
    user = get_request_user()
    if not user:
        return None, get_auth_error_response()
    return user, None


def _normalize_course(record):
    if not isinstance(record, dict):
        return None
    name = str(record.get('name') or record.get('course') or record.get('course_name') or record.get('课程名') or '').strip()
    day = str(record.get('day') or record.get('weekday') or record.get('星期') or '').strip()
    time = str(record.get('time') or record.get('节次') or record.get('schedule') or '').strip()
    teacher = str(record.get('teacher') or record.get('教师') or '').strip()
    weeks = str(record.get('weeks') or record.get('week') or record.get('weeks_range') or '').strip() or '1-16周'
    credits = str(record.get('credits') or record.get('学分') or '').strip()
    if not name:
        return None
    return {'id': f'course_{uuid.uuid4().hex[:8]}', 'name': name, 'day': day, 'time': time, 'teacher': teacher, 'weeks': weeks, 'credits': credits}


def _build_courses(data):
    if isinstance(data, dict) and 'courses' in data and isinstance(data['courses'], list):
        raw_courses = data['courses']
    elif isinstance(data, list):
        raw_courses = data
    else:
        return []
    return [c for c in [_normalize_course(i) for i in raw_courses] if c]


def _generate_tasks(courses):
    templates = ['整理课程笔记并标记重点', '规划教材购买清单', '复习上次课程核心概念', '查找相关参考书籍', '准备下次课程预习', '组建学习小组讨论']
    tasks = []
    for idx, course in enumerate(courses):
        count = min(3, max(1, math.ceil(len(course['name']) / 8)))
        for i in range(count):
            tasks.append({'id': f'task_{course["id"]}_{i}', 'course': course['name'], 'content': templates[(idx + i) % len(templates)], 'priority': ['high', 'medium', 'low'][(idx + i) % 3]})
    return tasks


def _generate_graph(courses):
    if not courses:
        return {'nodes': [], 'links': []}
    nodes, links = [], []
    base = 2 * math.pi / len(courses)
    for i, c in enumerate(courses):
        angle = base * i
        nodes.append({'id': c['id'], 'name': c['name'], 'category': 'course', 'symbolSize': 60, 'x': round(200 + math.cos(angle) * 150, 2), 'y': round(200 + math.sin(angle) * 150, 2), 'style': {'color': '#3b82f6'}})
    for i in range(len(courses)):
        links.append({'source': courses[i]['id'], 'target': courses[(i + 1) % len(courses)]['id'], 'lineStyle': {'width': 1.2, 'color': '#94a3b8', 'curveness': 0.1}})
    return {'nodes': nodes, 'links': links}


from .schedule_helpers import suggest_books


def _suggest_books(courses):
    return suggest_books(courses)


def _build_payload(courses):
    tasks = _generate_tasks(courses)
    graph = _generate_graph(courses)
    books = _suggest_books(courses)
    return {'courses': courses, 'tasks': tasks, 'graph': graph, 'related_books': books, 'summary': {'total_courses': len(courses), 'total_tasks': len(tasks), 'total_nodes': len(graph['nodes']), 'related_books_count': len(books)}}


def _read_json(file):
    try:
        return json.loads(file.read().decode('utf-8'))
    except Exception:
        return None


@schedule_bp.route('/api/schedule/parse', methods=['POST'])
def parse_schedule_file():
    if 'file' not in request.files:
        return error_response('请上传课程文件', 400)
    file = request.files['file']
    if not file.filename:
        return error_response('文件名不能为空', 400)
    if not file.filename.lower().endswith('.json'):
        return error_response('仅支持 JSON 文件', 400)
    data = _read_json(file)
    if data is None:
        return error_response('无法解析 JSON', 400)
    courses = _build_courses(data)
    if not courses:
        return error_response('未能提取课程信息', 400)
    return success_response(_build_payload(courses), '解析成功')


@schedule_bp.route('/api/schedule/manual', methods=['POST'])
def submit_manual_courses():
    data = request.get_json(silent=True) or {}
    raw = data.get('courses')
    if not isinstance(raw, list) or len(raw) == 0:
        return error_response('请提供课程列表', 400)
    courses = _build_courses(raw)
    if not courses:
        return error_response('课程格式不正确', 400)
    return success_response(_build_payload(courses), '生成成功')


@schedule_bp.route('/api/timetable/upload-file', methods=['POST'])
def upload_timetable_file():
    if 'file' not in request.files:
        return error_response('请上传课程文件', 400)
    file = request.files['file']
    if not file.filename:
        return error_response('文件名不能为空', 400)
    if not file.filename.lower().endswith('.json'):
        return error_response('仅支持 JSON 课表', 400)
    data = _read_json(file)
    if data is None:
        return error_response('无法解析 JSON', 400)
    courses = _build_courses(data)
    if not courses:
        return error_response('未能提取课程信息', 400)
    return success_response(_build_payload(courses), '上传成功')


@schedule_bp.route('/api/schedule/mock', methods=['POST'])
def generate_mock_schedule():
    """生成模拟课表数据，供一键体验使用"""
    mock_courses = [
        {'name': '高等数学', 'day': '周一', 'time': '1-2节', 'teacher': '张教授', 'weeks': '1-16周', 'credits': '5'},
        {'name': '线性代数', 'day': '周二', 'time': '3-4节', 'teacher': '李教授', 'weeks': '1-16周', 'credits': '3'},
        {'name': '大学英语', 'day': '周三', 'time': '1-2节', 'teacher': '王老师', 'weeks': '1-16周', 'credits': '4'},
        {'name': '程序设计基础', 'day': '周四', 'time': '5-6节', 'teacher': '赵教授', 'weeks': '1-16周', 'credits': '4'},
        {'name': '大学物理', 'day': '周五', 'time': '3-4节', 'teacher': '钱教授', 'weeks': '1-16周', 'credits': '4'},
    ]
    courses = _build_courses(mock_courses)
    return success_response(_build_payload(courses), '模拟课表生成成功')
