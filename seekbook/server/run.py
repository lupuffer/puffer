#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import app, db
from config import Config
from init_data import init_database


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_database(app)
        print('数据库初始化完成')

    print('=' * 50)
    print('SeekBook Flask 后端服务启动中...')
    print(f'API 地址: http://127.0.0.1:{Config.PORT}/api')
    print('代码修改后会自动重载后端')
    print('=' * 50)

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        use_reloader=True,
    )
