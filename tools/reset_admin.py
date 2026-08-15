import argparse
import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.extensions import db
from app.models.user import User


def main():
    parser = argparse.ArgumentParser(description='Reset the admin account password')
    parser.add_argument('--username', default='admin')
    parser.add_argument('--email', default='admin@srms.local')
    parser.add_argument('--password', default='123456')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(username=args.username).first()
        if admin is None:
            admin = User(username=args.username, email=args.email, role='admin')
            db.session.add(admin)

        admin.username = args.username
        admin.email = args.email
        admin.role = 'admin'
        admin.set_password(args.password)
        admin.force_password_change = False
        db.session.commit()

        print(f"Admin account synced for database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print(f'Username: {admin.username}')
        print(f'Password: {args.password}')


if __name__ == '__main__':
    main()
