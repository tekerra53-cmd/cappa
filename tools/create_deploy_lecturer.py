import sys
import os
import argparse

# Ensure project root is importable
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app
from app.admin.services import create_user


def main():
    parser = argparse.ArgumentParser(description='Create a lecturer user in the target environment')
    parser.add_argument('--username', required=True)
    parser.add_argument('--email', required=True)
    parser.add_argument('--password', required=False, default='ChangeMe123!')
    parser.add_argument('--role', required=False, default='lecturer')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        try:
            u = create_user(args.username, args.email, args.password, args.role)
            print(f'Created user: {u.id} {u.username} ({u.role})')
        except Exception as e:
            print('Error:', e)


if __name__ == '__main__':
    main()
