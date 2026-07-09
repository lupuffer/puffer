"""提供智慧清单模拟书籍数据与推荐逻辑"""
from models import Book

# 库存封面图片池（避免全部落回同一张 book1.jpg）
_IMAGE_POOL = [f'/images/book{i}.jpg' for i in range(1, 7)]  # book1~book6

_MOCK_BOOK_TITLES = [
    {'title': '高等数学（第七版）上册', 'author': '同济大学数学系', 'publisher': '高等教育出版社', 'isbn': '9787040396638', 'subject': '数学', 'price': 46.00},
    {'title': '高等数学（第七版）下册', 'author': '同济大学数学系', 'publisher': '高等教育出版社', 'isbn': '9787040396621', 'subject': '数学', 'price': 43.00},
    {'title': '线性代数及其应用（第五版）', 'author': 'David C. Lay', 'publisher': '机械工业出版社', 'isbn': '9787111574279', 'subject': '数学', 'price': 59.00},
    {'title': '新视野大学英语（第三版）读写教程1', 'author': '郑树棠', 'publisher': '外语教学与研究出版社', 'isbn': '9787513596008', 'subject': '英语', 'price': 49.90},
    {'title': '新视野大学英语（第三版）读写教程2', 'author': '郑树棠', 'publisher': '外语教学与研究出版社', 'isbn': '9787513596022', 'subject': '英语', 'price': 49.90},
    {'title': 'C Primer Plus（第6版）中文版', 'author': 'Stephen Prata', 'publisher': '人民邮电出版社', 'isbn': '9787115390592', 'subject': '计算机', 'price': 89.00},
    {'title': 'C程序设计语言（第2版）', 'author': 'Brian W. Kernighan', 'publisher': '机械工业出版社', 'isbn': '9787111196266', 'subject': '计算机', 'price': 39.00},
    {'title': 'Python编程：从入门到实践（第3版）', 'author': 'Eric Matthes', 'publisher': '人民邮电出版社', 'isbn': '9787115556278', 'subject': '计算机', 'price': 89.00},
    {'title': '大学物理（第四版）上册', 'author': '马文蔚', 'publisher': '高等教育出版社', 'isbn': '9787040136364', 'subject': '物理', 'price': 47.50},
    {'title': '大学物理（第四版）下册', 'author': '马文蔚', 'publisher': '高等教育出版社', 'isbn': '9787040136357', 'subject': '物理', 'price': 45.80},
    {'title': '数据结构（C语言版 第3版）', 'author': '严蔚敏', 'publisher': '清华大学出版社', 'isbn': '9787302330646', 'subject': '计算机', 'price': 49.00},
    {'title': '计算机组成原理（第3版）', 'author': '唐朔飞', 'publisher': '高等教育出版社', 'isbn': '9787040545180', 'subject': '计算机', 'price': 52.00},
    {'title': '数据库系统概论（第5版）', 'author': '王珊', 'publisher': '高等教育出版社', 'isbn': '9787040406641', 'subject': '计算机', 'price': 42.00},
    {'title': 'Java核心技术 卷I', 'author': 'Cay S. Horstmann', 'publisher': '机械工业出版社', 'isbn': '9787111636660', 'subject': '计算机', 'price': 119.00},
    {'title': '概率论与数理统计（第5版）', 'author': '浙江大学', 'publisher': '高等教育出版社', 'isbn': '9787040516609', 'subject': '数学', 'price': 39.80},
    {'title': '微观经济学：现代观点', 'author': 'Hal R. Varian', 'publisher': '格致出版社', 'isbn': '9787543233058', 'subject': '经济管理', 'price': 69.00},
    {'title': '管理学（第15版）', 'author': 'Stephen P. Robbins', 'publisher': '中国人民大学出版社', 'isbn': '9787300300795', 'subject': '经济管理', 'price': 68.00},
    {'title': '基础会计学', 'author': '朱小平', 'publisher': '中国人民大学出版社', 'isbn': '9787300294315', 'subject': '经济管理', 'price': 45.00},
    {'title': '统计学（第8版）', 'author': '贾俊平', 'publisher': '中国人民大学出版社', 'isbn': '9787300293103', 'subject': '经济管理', 'price': 56.00},
]


def _market_books_query():
    return Book.query.filter(Book.status == 'on_sale')


def _course_keyword(course):
    """从课程名推导搜索关键词"""
    name = (course.get('name') or '').strip()
    keywords = [name]
    if '数学' in name or '高数' in name or '代数' in name:
        keywords.extend(['数学', '高等数学', '线性代数'])
    elif '概率' in name or '统计' in name:
        keywords.extend(['概率论', '统计学', '数学'])
    elif '英语' in name or '外语' in name:
        keywords.extend(['英语', '大学英语', '新视野'])
    elif '经济' in name:
        keywords.extend(['经济学', '微观经济学', '经济管理'])
    elif '管理' in name:
        keywords.extend(['管理学', '经济管理'])
    elif '会计' in name:
        keywords.extend(['会计学', '基础会计', '经济管理'])
    elif '数据库' in name:
        keywords.extend(['数据库', '数据库系统', '计算机'])
    elif '数据结构' in name:
        keywords.extend(['数据结构', '计算机'])
    elif '组成原理' in name:
        keywords.extend(['计算机组成', '组成原理', '计算机'])
    elif '软件工程' in name:
        keywords.extend(['软件工程', '实践者', '计算机'])
    elif '前端' in name or 'Web' in name or '网页' in name:
        keywords.extend(['前端', 'HTML', 'CSS', '网页', '原型'])
    elif '操作系统' in name:
        keywords.extend(['操作系统', '现代操作系统', '计算机'])
    elif '计算机网络' in name:
        keywords.extend(['计算机网络', '自顶向下', '网络'])
    elif '项目管理' in name:
        keywords.extend(['项目管理', '软件项目管理'])
    elif 'Java' in name:
        keywords.extend(['Java', '程序设计', '计算机'])
    elif '视觉传达' in name:
        keywords.extend(['视觉传达', '设计'])
    elif '用户体验' in name:
        keywords.extend(['用户体验', 'UX', '设计'])
    elif '数字媒体' in name:
        keywords.extend(['数字媒体', '媒体技术'])
    elif '摄影' in name:
        keywords.extend(['摄影', '摄影基础'])
    elif '程序' in name or 'C语言' in name or '编程' in name or 'Python' in name or 'Java' in name:
        keywords.extend(['计算机', '程序设计', '编程'])
    elif '物理' in name:
        keywords.extend(['物理', '大学物理'])
    return keywords


def _fallback_book_dict(mock, idx=0):
    """当数据库无匹配时从 mock 数据构造书籍字典（使用多样化封面图片与有效 ID）"""
    image = _IMAGE_POOL[idx % len(_IMAGE_POOL)]
    return {
        'id': None, 'title': mock['title'], 'author': mock['author'],
        'publisher': mock['publisher'], 'isbn': mock['isbn'],
        'price': mock['price'], 'subject': mock['subject'],
        'cover': image, 'coverImage': image,
        'images': [image], 'status': 'on_sale',
    }


def _ensure_cover(b):
    """确保书籍字典包含 cover 字段"""
    if 'cover' not in b:
        b['cover'] = b.get('coverImage') or (b.get('images') or [''])[0] or '/images/book1.jpg'
    if 'id' not in b:
        b['id'] = None


def _matches_mock(course, mock):
    haystack = f"{mock['title']} {mock['subject']} {mock['author']} {mock['publisher']}"
    return any(kw and kw in haystack for kw in _course_keyword(course))


def suggest_books(courses):
    """根据课程列表推荐相关的书籍（优先数据库 + 模拟兜底）"""
    if not courses:
        return []
    suggested = []
    seen_isbns = set()

    for course_index, course in enumerate(courses):
        course_name = (course.get('name') or '').strip()
        keywords = _course_keyword(course)
        course_added = 0

        if course_name:
            exact_books = _market_books_query().filter(
                (Book.subject == course_name) | (Book.title.contains(course_name))
            ).order_by(Book.created_at.desc()).limit(1).all()
            for b in exact_books:
                d = b.to_dict()
                if d.get('isbn') not in seen_isbns:
                    seen_isbns.add(d.get('isbn'))
                    _ensure_cover(d)
                    suggested.append(d)
                    course_added = 1
                    break

        if course_added:
            if len(suggested) >= 6:
                break
            continue

        for kw in keywords:
            books = _market_books_query().filter(
                (Book.subject.contains(kw)) | (Book.title.contains(kw))
            ).order_by(Book.created_at.desc()).limit(1).all()
            for b in books:
                d = b.to_dict()
                if d.get('isbn') not in seen_isbns:
                    seen_isbns.add(d.get('isbn'))
                    _ensure_cover(d)
                    suggested.append(d)
                    course_added += 1
                    if course_added >= 1 or len(suggested) >= 6:
                        break
            if course_added >= 1 or len(suggested) >= 6:
                break

        if course_added == 0:
            for idx, mock in enumerate(_MOCK_BOOK_TITLES):
                if not _matches_mock(course, mock):
                    continue
                isbn = mock['isbn']
                if isbn in seen_isbns:
                    continue
                existing = _market_books_query().filter(Book.isbn == isbn).first()
                d = existing.to_dict() if existing else _fallback_book_dict(mock, course_index + idx)
                seen_isbns.add(isbn)
                d['isbn'] = isbn
                _ensure_cover(d)
                suggested.append(d)
                break

        if len(suggested) >= 6:
            break

    return suggested
