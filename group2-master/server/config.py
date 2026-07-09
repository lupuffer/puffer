import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _parse_csv_env(name, default_values):
    value = os.getenv(name, '').strip()
    if not value:
        return default_values
    return [item.strip() for item in value.split(',') if item.strip()]


class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'seekbook.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'seekbook-dev-secret-change-me')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ISSUER = os.getenv('JWT_ISSUER', 'seekbook-server')
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES_HOURS', '2'))
    JWT_REFRESH_TOKEN_EXPIRES_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES_DAYS', '5'))

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    CORS_ORIGINS = _parse_csv_env(
        'CORS_ORIGINS',
        [
            'http://localhost:5173',
            'http://127.0.0.1:5173',
            'http://localhost:4173',
            'http://127.0.0.1:4173',
        ],
    )

    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '5000'))
    DEBUG = os.getenv('FLASK_DEBUG', '1') != '0'

    DEFAULT_USER_ID = 'user_001'
    DEFAULT_USER_NAME = '用户001'
