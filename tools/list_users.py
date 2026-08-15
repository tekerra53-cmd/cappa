import sys
import os

# Ensure project root is importable when running as a script
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import create_app

app = create_app()
with app.app_context():
    from app.models.user import User
    users = User.query.order_by(User.id).all()
    for u in users:
        print(u.id, u.username, repr(u.role))
