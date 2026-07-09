from datetime import datetime
from werkzeug.security import generate_password_hash
from models import db, User, Note, KnowledgeMaterial, KnowledgeDiscussion, KnowledgeComment, KnowledgeMaterialFavorite, KnowledgeMaterialEntitlement, KnowledgeMaterialLike, KnowledgeDiscussionLike, KnowledgeCheckIn, KnowledgePointLedger, KnowledgeRank

DEFAULT_PASSWORD = '123456'

DEFAULT_KNOWLEDGE_MATERIALS = [
    {
        'title': '高等数学期末冲刺题集',
        'category': '公共课',
        'course_name': 'MATH101 高等数学',
        'description': '整理了常见题型、易错点和压轴题思路，适合期末一周集中复习。',
        'price_points': 0,
        'file_type': 'PDF',
        'file_size': '2.5MB',
        'tags': '期末复习,高数,真题',
    },
    {
        'title': '数据结构实验报告模板',
        'category': '专业课',
        'course_name': 'CS203 数据结构',
        'description': '包含链表、栈队列、图结构实验报告模板和常见评分点提醒。',
        'price_points': 5,
        'file_type': 'Word',
        'file_size': '860KB',
        'tags': '实验报告,数据结构',
    },
    {
        'title': '考研英语阅读精练笔记',
        'category': '考研',
        'course_name': '考研英语',
        'description': '按题型整理的阅读笔记，包含长难句拆解和高频词组速记。',
        'price_points': 10,
        'file_type': 'PDF',
        'file_size': '1.6MB',
        'tags': '考研,英语,阅读',
    },
    {
        'title': '离散数学思维导图合集',
        'category': '课堂笔记',
        'course_name': 'CS112 离散数学',
        'description': '章节思维导图和证明题套路总结，适合课后回顾和开卷复习。',
        'price_points': 0,
        'file_type': '图片',
        'file_size': '1.1MB',
        'tags': '离散数学,思维导图',
    },
    {
        'title': '计算机组成原理章节速查表',
        'category': '专业课',
        'course_name': '计算机组成原理',
        'description': '覆盖数据表示、运算器、存储系统、指令系统与流水线的课堂速查笔记。',
        'price_points': 5,
        'file_type': 'PDF',
        'file_size': '1.3MB',
        'tags': '组成原理,速查表,计算机',
    },
    {
        'title': '概率论与数理统计公式卡片',
        'category': '公共课',
        'course_name': '概率论与数理统计',
        'description': '按分布、数字特征、参数估计、假设检验整理常用公式和易混点。',
        'price_points': 0,
        'file_type': 'PDF',
        'file_size': '980KB',
        'tags': '概率论,统计,公式',
    },
    {
        'title': '数据库系统 SQL 实验清单',
        'category': '专业课',
        'course_name': '数据库系统',
        'description': '包含建表、查询、视图、事务与索引实验的检查清单和常见错误说明。',
        'price_points': 5,
        'file_type': 'Word',
        'file_size': '760KB',
        'tags': '数据库,SQL,实验',
    },
    {
        'title': 'Java 程序设计课堂样例合集',
        'category': '专业课',
        'course_name': 'Java程序设计',
        'description': '整理面向对象、集合、异常、IO 与简单 Swing 示例代码，适合课后补齐练习。',
        'price_points': 8,
        'file_type': '压缩包',
        'file_size': '1.9MB',
        'tags': 'Java,样例代码,程序设计',
    },
    {
        'title': '微观经济学图形题整理',
        'category': '专业课',
        'course_name': '微观经济学',
        'description': '需求供给、消费者选择、成本曲线、市场结构相关图形题和答题模板。',
        'price_points': 5,
        'file_type': 'PDF',
        'file_size': '1.2MB',
        'tags': '微观经济学,图形题,经管',
    },
    {
        'title': '管理学原理案例分析模板',
        'category': '专业课',
        'course_name': '管理学原理',
        'description': '按计划、组织、领导、控制四类管理职能整理案例分析框架。',
        'price_points': 0,
        'file_type': 'Word',
        'file_size': '640KB',
        'tags': '管理学,案例分析',
    },
    {
        'title': '会计学基础分录练习表',
        'category': '专业课',
        'course_name': '会计学基础',
        'description': '按资产、负债、所有者权益、收入费用整理会计分录练习与答案。',
        'price_points': 5,
        'file_type': 'Excel',
        'file_size': '520KB',
        'tags': '会计学,分录,练习',
    },
    {
        'title': '统计学 SPSS 操作笔记',
        'category': '专业课',
        'course_name': '统计学',
        'description': '描述统计、相关分析、回归分析和假设检验的 SPSS 操作步骤截图版笔记。',
        'price_points': 8,
        'file_type': 'PDF',
        'file_size': '1.7MB',
        'tags': '统计学,SPSS,数据分析',
    },
    {
        'title': '大学英语听力课堂材料',
        'category': '公共课',
        'course_name': '大学英语',
        'description': '课堂听力音频文本、关键词表和课后跟读材料，适合大学英语课程使用。',
        'price_points': 0,
        'file_type': 'PDF',
        'file_size': '900KB',
        'tags': '大学英语,听力,课堂材料',
    },
]


def ensure_default_knowledge_materials():
    existing_titles = {
        title for (title,) in db.session.query(KnowledgeMaterial.title).filter_by(status='active').all()
    }
    missing = []
    for item in DEFAULT_KNOWLEDGE_MATERIALS:
        if item['title'] in existing_titles:
            continue
        missing.append(KnowledgeMaterial(
            title=item['title'],
            description=item['description'],
            file_type=item['file_type'],
            file_size=item['file_size'],
            category=item['category'],
            course_name=item['course_name'],
            tags=item['tags'],
            price_points=item['price_points'],
            download_count=0,
            like_count=0,
            view_count=0,
            uploader_id='seller_001',
            status='active',
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        ))

    if missing:
        db.session.bulk_save_objects(missing)


def seed_users():
    if User.query.count() > 0:
        return
    import random
    pwd = generate_password_hash(DEFAULT_PASSWORD)
    users = [
        User(id='user_001', username='user_001', email='user_001@seekbook.local', name='Buyer One', password_hash=pwd, role='buyer', reputation='A', credit_score=random.randint(90, 100), points_balance=30),
        User(id='user_002', username='user_002', email='user_002@seekbook.local', name='Buyer Two', password_hash=pwd, role='buyer', reputation='B', credit_score=random.randint(80, 95), points_balance=15),
        User(id='user_003', username='user_003', email='user_003@seekbook.local', name='Buyer Three', password_hash=pwd, role='buyer', reputation='A', credit_score=random.randint(90, 100), points_balance=10),
        User(id='seller_001', username='seller_001', email='seller_001@seekbook.local', name='Seller A', password_hash=pwd, role='seller', reputation='A', credit_score=random.randint(95, 105), points_balance=20),
        User(id='seller_002', username='seller_002', email='seller_002@seekbook.local', name='Seller B', password_hash=pwd, role='seller', reputation='A', credit_score=random.randint(92, 102), points_balance=20),
        User(id='seller_003', username='seller_003', email='seller_003@seekbook.local', name='Seller C', password_hash=pwd, role='seller', reputation='B', credit_score=random.randint(80, 92), points_balance=10),
        User(id='seller_004', username='seller_004', email='seller_004@seekbook.local', name='Seller D', password_hash=pwd, role='seller', reputation='A', credit_score=random.randint(90, 100), points_balance=10),
        User(id='seller_005', username='seller_005', email='seller_005@seekbook.local', name='Seller E', password_hash=pwd, role='seller', reputation='B', credit_score=random.randint(82, 95), points_balance=10),
    ]
    db.session.bulk_save_objects(users)
    db.session.commit()


def seed_notes():
    if Note.query.count() > 0:
        return
    notes = [
        Note(title='Calculus final review highlights', content='Focus on limits, derivatives and integrals first.', author_id='user_001', book_id=1, likes=128, views=860, tags='math,review,final'),
        Note(title='Computer network study roadmap', content='Start from the layered model, then work through TCP/IP.', author_id='user_002', book_id=2, likes=96, views=640, tags='network,course-summary'),
        Note(title='Data structure practice advice', content='Split linked list, tree and graph problems into stages.', author_id='user_003', book_id=3, likes=143, views=910, tags='data-structure,algorithm'),
    ]
    db.session.bulk_save_objects(notes)
    db.session.commit()


def seed_knowledge_data():
    today = datetime.utcnow().strftime('%Y-%m-%d')

    if KnowledgeMaterial.query.count() == 0:
        db.session.bulk_save_objects([
            KnowledgeMaterial(title='Calculus review pack', description='Includes formula sheets and past-paper notes.', file_type='pdf', file_size='15.2MB', category='math', course_name='Advanced Mathematics', tags='final-review,calculus', price_points=0, download_count=342, like_count=118, view_count=820, uploader_id='seller_001'),
            KnowledgeMaterial(title='CET audio preparation bundle', description='Suitable for midterm review and CET listening practice.', file_type='zip', file_size='128.5MB', category='english', course_name='College English', tags='cet,listening', price_points=10, download_count=275, like_count=94, view_count=610, uploader_id='seller_002'),
        ])

    ensure_default_knowledge_materials()

    if KnowledgeDiscussion.query.count() == 0:
        db.session.bulk_save_objects([
            KnowledgeDiscussion(discussion_type='讨论', title='For second-round calculus review, should I brush questions first or revisit mistakes first?', content='I am preparing for finals and want to know what helped others most.', tags='calculus,final', author_id='user_001', like_count=9, reply_count=2),
            KnowledgeDiscussion(discussion_type='求助', title='How do you fix permission errors in the operating systems lab setup?', content='The Windows environment keeps failing with permission errors.', tags='os,lab', author_id='user_002', like_count=12, reply_count=1),
        ])

    if KnowledgeComment.query.count() == 0:
        db.session.bulk_save_objects([
            KnowledgeComment(target_type='discussion', target_id=1, author_id='user_003', content='I usually redo mistakes first, then brush topic-based exercises.'),
            KnowledgeComment(target_type='discussion', target_id=1, author_id='seller_001', content='Separating definition problems from proof problems helps a lot.'),
            KnowledgeComment(target_type='discussion', target_id=2, author_id='seller_002', content='Try opening the terminal as admin first and check folder permissions.'),
        ])

    if KnowledgeMaterialFavorite.query.count() == 0:
        db.session.bulk_save_objects([
            KnowledgeMaterialFavorite(user_id='user_001', material_id=1),
            KnowledgeMaterialFavorite(user_id='user_002', material_id=2),
        ])

    if KnowledgeMaterialEntitlement.query.count() == 0:
        db.session.bulk_save_objects([
            KnowledgeMaterialEntitlement(user_id='user_001', material_id=2, source='download'),
        ])

    if KnowledgeMaterialLike.query.count() == 0:
        db.session.bulk_save_objects([
            KnowledgeMaterialLike(user_id='user_001', material_id=1),
            KnowledgeMaterialLike(user_id='user_002', material_id=2),
        ])

    if KnowledgeDiscussionLike.query.count() == 0:
        db.session.bulk_save_objects([
            KnowledgeDiscussionLike(user_id='user_001', discussion_id=1),
            KnowledgeDiscussionLike(user_id='user_002', discussion_id=2),
        ])

    if KnowledgeCheckIn.query.count() == 0:
        db.session.bulk_save_objects([KnowledgeCheckIn(user_id='user_001', checkin_date=today)])

    if KnowledgePointLedger.query.count() == 0:
        db.session.bulk_save_objects([
            KnowledgePointLedger(user_id='user_001', action='daily_checkin', delta=5, balance_after=30, note='每日签到'),
            KnowledgePointLedger(user_id='user_001', action='download_material', delta=-10, balance_after=25, reference_type='material', reference_id=2, note='下载资料 CET audio preparation bundle'),
            KnowledgePointLedger(user_id='user_002', action='upload_material', delta=10, balance_after=15, reference_type='material', reference_id=2, note='上传资料奖励'),
        ])

    if KnowledgeRank.query.count() == 0:
        db.session.bulk_save_objects([
            KnowledgeRank(user_id='seller_001', rank_type='upload', score=156, period='month'),
            KnowledgeRank(user_id='seller_002', rank_type='upload', score=128, period='month'),
            KnowledgeRank(user_id='seller_003', rank_type='upload', score=98, period='month'),
        ])

    db.session.commit()
