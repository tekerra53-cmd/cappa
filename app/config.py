import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
INSTANCE_DIR = BASE_DIR / 'instance'


def _resolve_db_path():
    database_url = os.environ.get('DATABASE_URL', '').strip()
    if database_url.startswith('sqlite:///'):
        sqlite_path = database_url[len('sqlite:///'):]
        if sqlite_path.startswith('/'):
            return Path(sqlite_path)
        return (BASE_DIR / sqlite_path).resolve()

    env_db_path = os.environ.get('APP_DB_PATH', '').strip()
    if env_db_path:
        db_path = Path(env_db_path).expanduser()
        if not db_path.is_absolute():
            db_path = (BASE_DIR / db_path).resolve()
        return db_path

    return (INSTANCE_DIR / 'app.db').resolve()


DB_PATH = _resolve_db_path()

# Ensure instance directory exists
DB_PATH.parent.mkdir(exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-string')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH.as_posix()}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
