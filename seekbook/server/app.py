from flask import Flask, send_from_directory
from flask_cors import CORS
import os

from config import Config
from models import db
from init_data import init_database

# 导入蓝图
from views.books import books_bp
from views.chats import chats_bp
from views.auth import auth_bp
from views.favorites import favorites_bp
from views.notes import notes_bp
from views.orders import orders_bp
from views.orders_actions import orders_actions_bp
from views.orders_reviews import orders_reviews_bp
from views.schedule import schedule_bp
from views.uploads import uploads_bp
from views.isbn_ocr import isbn_ocr_bp
from views.knowledge import knowledge_bp
from views.drafts import drafts_bp
from views.shortage_registrations import shortage_registrations_bp
from views.notifications import notifications_bp
from views.user_profile import user_profile_bp
from views.user_stats import user_stats_bp

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

    # 确保上传目录存在
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

    # 注册蓝图（核心功能：书籍、聊天、认证、收藏、笔记、订单、课表、上传、OCR、知识库）
    app.register_blueprint(books_bp)
    app.register_blueprint(chats_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(orders_actions_bp)
    app.register_blueprint(orders_reviews_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(uploads_bp)
    app.register_blueprint(isbn_ocr_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(drafts_bp)
    app.register_blueprint(shortage_registrations_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(user_profile_bp)
    app.register_blueprint(user_stats_bp)

    # 静态文件服务
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(Config.UPLOAD_FOLDER, filename)

    # 健康检查
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'code': 200, 'message': 'ok', 'data': {'status': 'running'}}

    @app.route('/api/data/catalog', methods=['GET'])
    def data_catalog():
        from models import Book
        books = Book.query.filter_by(status='on_sale').order_by(Book.created_at.desc()).all()
        return {'code': 200, 'message': 'ok', 'data': {
            'books': [book.to_dict() for book in books],
            'total': len(books),
        }}

    @app.route('/api/init', methods=['POST'])
    def api_init_database():
        init_database(app)
        return {'code': 200, 'message': '数据库初始化完成', 'data': None}

    # 确保每次请求后关闭数据库连接，防止连接泄漏
    @app.teardown_request
    def remove_session(exception=None):
        db.session.remove()

    with app.app_context():
        db.create_all()
        init_database(app)

    return app

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, use_reloader=True)