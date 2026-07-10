from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)
    role = db.Column(db.String(20), nullable=False)
    is_advisor = db.Column(db.Boolean, nullable=False, default=False)
    advisor_level = db.Column(db.String(10), nullable=True)
    force_password_change = db.Column(db.Boolean, nullable=False, default=False)
    student_profile = db.relationship('Student', backref='user', uselist=False)
    courses = db.relationship('Course', backref='lecturer', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def generate_random_password(length=12):
        import secrets, string
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))
