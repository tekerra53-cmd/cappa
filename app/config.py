import os
import re
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / '.env', override=True)

INSTANCE_DIR = BASE_DIR / 'instance'
SERVERLESS_DB_PATH = Path('/tmp') / 'cappa_app.db'


def _resolve_db_path():
    database_url = os.environ.get('DATABASE_URL', '').strip()
    if database_url.startswith('sqlite:///'):
        sqlite_path = database_url[len('sqlite:///'):]
        if not sqlite_path:
            return (INSTANCE_DIR / 'app.db').resolve()
        if sqlite_path.startswith('/'):
            return Path(sqlite_path)
        if re.match(r'^[A-Za-z]:[\\/]', sqlite_path):
            return Path(sqlite_path)
        return (BASE_DIR / sqlite_path).resolve()

    env_db_path = os.environ.get('APP_DB_PATH', '').strip()
    if env_db_path:
        db_path = Path(env_db_path).expanduser()
        if not db_path.is_absolute():
            db_path = (BASE_DIR / db_path).resolve()
        return db_path

    if os.environ.get('VERCEL') or os.environ.get('RENDER') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME'):
        return SERVERLESS_DB_PATH

    return (INSTANCE_DIR / 'app.db').resolve()


def _build_sqlalchemy_uri(database_url):
    if database_url.startswith('sqlite:///'):
        sqlite_path = database_url[len('sqlite:///'):]
        if not sqlite_path:
            db_path = (INSTANCE_DIR / 'app.db').resolve()
        elif sqlite_path.startswith('/'):
            db_path = Path(sqlite_path)
        elif re.match(r'^[A-Za-z]:[\\/]', sqlite_path):
            db_path = Path(sqlite_path)
        else:
            db_path = (BASE_DIR / sqlite_path).resolve()
        db_path.parent.mkdir(exist_ok=True)
        return f'sqlite:///{db_path.as_posix()}'
    return database_url


DB_PATH = _resolve_db_path()

# Ensure instance directory exists for local SQLite fallback
if os.environ.get('DATABASE_URL', '').startswith('sqlite:///'):
    DB_PATH.parent.mkdir(exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-string')
    DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()
    SQLALCHEMY_DATABASE_URI = _build_sqlalchemy_uri(DATABASE_URL or f'sqlite:///{DB_PATH.as_posix()}')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
