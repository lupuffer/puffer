import json
from datetime import datetime

from models import Book, db

SCHEDULE_BOOK_TAG = 'schedule-demo'
SELLER_IDS = ['seller_001', 'seller_002', 'seller_003', 'seller_004', 'seller_005']
CAMPUSES = ['zijingang', 'yuquan', 'xixi', 'zhijiang', 'huajiachi']
CONDITIONS = ['like-new', 'good', 'new', 'like-new', 'good']

SCHEDULE_TEXTBOOKS = [
    # timetable_demo_01_computer_science
    {'course': '数据结构', 'title': '数据结构（C语言版 第3版）', 'author': '严蔚敏', 'publisher': '清华大学出版社', 'isbn': '9787302330646', 'price': 49.0, 'original_price': 59.0, 'image': '/images/book2.jpg'},
    {'course': '计算机组成原理', 'title': '计算机组成原理（第3版）', 'author': '唐朔飞', 'publisher': '高等教育出版社', 'isbn': '9787040545180', 'price': 52.0, 'original_price': 65.0, 'image': '/images/book3.jpg'},
    {'course': '概率论与数理统计', 'title': '概率论与数理统计（第5版）', 'author': '浙江大学', 'publisher': '高等教育出版社', 'isbn': '9787040516609', 'price': 39.8, 'original_price': 49.0, 'image': '/images/book4.jpg'},
    {'course': '数据库系统', 'title': '数据库系统概论（第5版）', 'author': '王珊', 'publisher': '高等教育出版社', 'isbn': '9787040406641', 'price': 42.0, 'original_price': 52.0, 'image': '/images/book5.jpg'},
    {'course': 'Java程序设计', 'title': 'Java核心技术 卷I', 'author': 'Cay S. Horstmann', 'publisher': '机械工业出版社', 'isbn': '9787111636660', 'price': 79.0, 'original_price': 119.0, 'image': '/images/book6.jpg'},

    # timetable_demo_02_software_engineering
    {'course': '软件工程', 'title': '软件工程：实践者的研究方法', 'author': 'Roger S. Pressman', 'publisher': '机械工业出版社', 'isbn': '9787111683947', 'price': 68.0, 'original_price': 89.0, 'image': '/images/book1.jpg'},
    {'course': 'Web前端开发', 'title': 'HTML5与CSS3基础教程', 'author': 'Julie C. Meloni', 'publisher': '人民邮电出版社', 'isbn': '9787115583571', 'price': 45.0, 'original_price': 59.8, 'image': '/images/book2.jpg'},
    {'course': '操作系统', 'title': '现代操作系统（第4版）', 'author': 'Andrew S. Tanenbaum', 'publisher': '机械工业出版社', 'isbn': '9787111573698', 'price': 72.0, 'original_price': 99.0, 'image': '/images/book3.jpg'},
    {'course': '计算机网络', 'title': '计算机网络：自顶向下方法', 'author': 'James F. Kurose', 'publisher': '机械工业出版社', 'isbn': '9787111599711', 'price': 76.0, 'original_price': 99.0, 'image': '/images/book4.jpg'},
    {'course': '项目管理与实践', 'title': '软件项目管理案例教程', 'author': '韩万江', 'publisher': '机械工业出版社', 'isbn': '9787111664540', 'price': 38.0, 'original_price': 49.0, 'image': '/images/book5.jpg'},

    # timetable_demo_03_business_management
    {'course': '微观经济学', 'title': '微观经济学：现代观点', 'author': 'Hal R. Varian', 'publisher': '格致出版社', 'isbn': '9787543233058', 'price': 69.0, 'original_price': 88.0, 'image': '/images/book1.jpg'},
    {'course': '管理学原理', 'title': '管理学（第15版）', 'author': 'Stephen P. Robbins', 'publisher': '中国人民大学出版社', 'isbn': '9787300300795', 'price': 68.0, 'original_price': 89.0, 'image': '/images/book2.jpg'},
    {'course': '会计学基础', 'title': '基础会计学', 'author': '朱小平', 'publisher': '中国人民大学出版社', 'isbn': '9787300294315', 'price': 45.0, 'original_price': 58.0, 'image': '/images/book3.jpg'},
    {'course': '大学英语', 'title': '新视野大学英语（第三版）读写教程2', 'author': '郑树棠', 'publisher': '外语教学与研究出版社', 'isbn': '9787513596022', 'price': 36.0, 'original_price': 49.9, 'image': '/images/book4.jpg'},
    {'course': '统计学', 'title': '统计学（第8版）', 'author': '贾俊平', 'publisher': '中国人民大学出版社', 'isbn': '9787300293103', 'price': 56.0, 'original_price': 72.0, 'image': '/images/book5.jpg'},

    # timetable_demo_04_design_media
    {'course': '视觉传达设计', 'title': '视觉传达设计原理', 'author': '王受之', 'publisher': '中国青年出版社', 'isbn': '9787515362229', 'price': 48.0, 'original_price': 68.0, 'image': '/images/book6.jpg'},
    {'course': '用户体验设计', 'title': '用户体验要素', 'author': 'Jesse James Garrett', 'publisher': '机械工业出版社', 'isbn': '9787111348665', 'price': 42.0, 'original_price': 59.0, 'image': '/images/book1.jpg'},
    {'course': '数字媒体技术', 'title': '数字媒体技术导论', 'author': '李四达', 'publisher': '清华大学出版社', 'isbn': '9787302575962', 'price': 39.0, 'original_price': 52.0, 'image': '/images/book2.jpg'},
    {'course': '摄影基础', 'title': '摄影基础教程', 'author': '郑虹', 'publisher': '中国摄影出版社', 'isbn': '9787517909620', 'price': 35.0, 'original_price': 49.0, 'image': '/images/book3.jpg'},
    {'course': '网页交互原型', 'title': 'Axure RP 9 网站与App原型设计', 'author': '李涛', 'publisher': '人民邮电出版社', 'isbn': '9787115530094', 'price': 46.0, 'original_price': 69.0, 'image': '/images/book4.jpg'},

    # timetable_demo_05_mixed_review
    {'course': '高等数学', 'title': '高等数学（第七版）上册', 'author': '同济大学数学系', 'publisher': '高等教育出版社', 'isbn': '9787040396638', 'price': 46.0, 'original_price': 58.0, 'image': '/images/book5.jpg'},
    {'course': '线性代数', 'title': '线性代数及其应用（第五版）', 'author': 'David C. Lay', 'publisher': '机械工业出版社', 'isbn': '9787111574279', 'price': 59.0, 'original_price': 79.0, 'image': '/images/book6.jpg'},
    {'course': '大学物理', 'title': '大学物理（第四版）上册', 'author': '马文蔚', 'publisher': '高等教育出版社', 'isbn': '9787040136364', 'price': 47.5, 'original_price': 62.0, 'image': '/images/book1.jpg'},
    {'course': 'Python程序设计', 'title': 'Python编程：从入门到实践（第3版）', 'author': 'Eric Matthes', 'publisher': '人民邮电出版社', 'isbn': '9787115556278', 'price': 69.0, 'original_price': 89.0, 'image': '/images/book2.jpg'},
]


def _mapping(item, index):
    now = datetime.utcnow()
    tags = f'{SCHEDULE_BOOK_TAG},{item["course"]},教材'
    return {
        'title': item['title'],
        'author': item['author'],
        'publisher': item['publisher'],
        'edition': '课程推荐版',
        'isbn': item['isbn'],
        'condition': CONDITIONS[index % len(CONDITIONS)],
        'has_notes': index % 3 == 0,
        'price': item['price'],
        'original_price': item['original_price'],
        'trade_method': 'face',
        'campus': CAMPUSES[index % len(CAMPUSES)],
        'contact': 'schedule-demo@seekbook.local',
        'images': json.dumps([item['image']]),
        'tags': tags,
        'description': f'{item["course"]} 课程推荐教材，供智慧清单演示使用。',
        'subject': item['course'],
        'grade': 'undergraduate',
        'book_type': 'textbook',
        'status': 'on_sale',
        'seller_id': SELLER_IDS[index % len(SELLER_IDS)],
        'created_at': now,
        'updated_at': now,
    }


def seed_schedule_books():
    existing_isbns = {
        row.isbn
        for row in Book.query.filter(Book.isbn.in_([item['isbn'] for item in SCHEDULE_TEXTBOOKS])).all()
    }
    rows = [
        _mapping(item, index)
        for index, item in enumerate(SCHEDULE_TEXTBOOKS)
        if item['isbn'] not in existing_isbns
    ]
    if not rows:
        return 0

    db.session.bulk_insert_mappings(Book, rows)
    db.session.commit()
    return len(rows)
