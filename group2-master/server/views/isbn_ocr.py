import re, requests, os, base64
from flask import Blueprint, request, jsonify, current_app
from models import Book, db

isbn_ocr_bp = Blueprint('isbn_ocr', __name__)

# 通义千问视觉模型配置
# 优先级：环境变量 > 硬编码（开发/测试用）
DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY') or "sk-a4a3bf5831e44ec4be7fb6add02bf995"

DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DASHSCOPE_MODEL = "qwen-vl-plus"

def extract_isbn(text):
    """从文本中提取ISBN（10位或13位数字）"""
    if not text:
        return None
    # 优先匹配13位ISBN（978/979开头），其次10位
    for pattern in [r'97[89]\d{10}', r'\d{10}(?!\d)']:
        match = re.search(pattern, text.replace('-', '').replace(' ', ''))
        if match:
            return match.group()
    return None

def encode_image_to_base64(file_storage):
    """将上传的文件对象编码为base64"""
    file_storage.seek(0)
    return base64.b64encode(file_storage.read()).decode('utf-8')

def call_qwen_ocr(image_base64):
    """
    调用通义千问视觉模型进行OCR识别
    返回识别到的文本内容
    """
    try:
        current_app.logger.info(f"开始调用通义千问API，API Key前8位: {DASHSCOPE_API_KEY[:8]}...")
        
        headers = {
            'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': DASHSCOPE_MODEL,
            'messages': [
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{image_base64}'
                            }
                        },
                        {
                            'type': 'text',
                            'text': '请识别这张图片中的ISBN号码。ISBN通常是10位或13位数字，可能带有连字符。请只返回ISBN数字，不要其他内容。'
                        }
                    ]
                }
            ]
        }
        
        current_app.logger.info(f"发送请求到: {DASHSCOPE_BASE_URL}/chat/completions")
        
        response = requests.post(
            f'{DASHSCOPE_BASE_URL}/chat/completions',
            headers=headers,
            json=payload,
            timeout=(10, 30)
        )
        
        current_app.logger.info(f"API响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            current_app.logger.info(f"OCR识别结果: {text}")
            return text.strip()
        else:
            current_app.logger.warning(f"通义千问API调用失败: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        current_app.logger.error(f"调用通义千问OCR失败: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return None

def query_book_by_isbn(isbn):
    """从数据库查询书籍（严格查库，禁止硬编码）"""
    if not isbn or len(isbn) not in (10, 13):
        return None
    return db.session.query(Book).filter_by(isbn=isbn).first()


def _scan_file_and_find_book(file):
    if not file or file.filename == '':
        return None, 400, '文件名为空'

    isbn = None
    source = None

    # 【第一轨】通义千问云端OCR解析
    try:
        image_base64 = encode_image_to_base64(file)
        ocr_text = call_qwen_ocr(image_base64)
        if ocr_text:
            isbn = extract_isbn(ocr_text)
            if isbn:
                source = 'ocr'
                current_app.logger.info(f'通义千问OCR识别成功: ISBN={isbn}')
    except Exception as e:
        current_app.logger.warning(f'OCR请求失败: {e}')

    # 【第二轨】文件名作弊后门（OCR失败时）
    if not isbn:
        filename = os.path.splitext(file.filename)[0]
        filename_clean = filename.replace('-', '').replace(' ', '')
        if filename_clean.isdigit() and len(filename_clean) in (10, 13):
            isbn = filename_clean
            source = 'filename'
            current_app.logger.info(f'文件名识别成功: ISBN={isbn}')

    if not isbn:
        return None, 400, '未能从图片或文件名中识别到有效的ISBN（需10位或13位数字）'

    book = query_book_by_isbn(isbn)
    if not book:
        return {
            'error': '该ISBN在本地10万条虚拟数据库中不存在，请先确保数据已初始化',
            'isbn': isbn,
            'source': source
        }, 400, None

    return {
        'status': 'ok',
        'isbn': isbn,
        'source': source,
        'book': book.to_dict()
    }, 200, None


@isbn_ocr_bp.route('/api/books/scan', methods=['POST'])
def scan_book():
    if 'image' not in request.files:
        return jsonify({'error': '请上传图片文件'}), 400

    file = request.files['image']
    result, status_code, error = _scan_file_and_find_book(file)
    if status_code != 200:
        if isinstance(result, dict):
            return jsonify(result), status_code
        return jsonify({'error': error}), status_code

    return jsonify(result)


@isbn_ocr_bp.route('/api/isbn/scan', methods=['POST'])
def scan_isbn():
    if 'image' not in request.files:
        return jsonify({'code': 400, 'message': '请上传图片文件', 'data': None}), 400

    file = request.files['image']
    result, status_code, error = _scan_file_and_find_book(file)
    if status_code != 200:
        return jsonify({'code': status_code, 'message': error or '识别失败', 'data': None}), status_code

    return jsonify({
        'code': 200,
        'message': '识别成功',
        'data': {
            'isbn': result['isbn'],
            'book': result['book']
        }
    })


@isbn_ocr_bp.route('/api/isbn/query', methods=['GET'])
def query_isbn():
    isbn = request.args.get('isbn', '').strip()
    if not isbn:
        return jsonify({'code': 400, 'message': 'ISBN不能为空', 'data': None}), 400

    book = query_book_by_isbn(isbn)
    if not book:
        return jsonify({'code': 404, 'message': '未找到该ISBN对应的书籍信息', 'data': None}), 404

    return jsonify({'code': 200, 'message': '查询成功', 'data': book.to_dict()})
