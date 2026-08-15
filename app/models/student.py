from ..extensions import db
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    # These imports are only for type checking (Pylance/mypy) and do not affect runtime
    from .user import User


class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(Integer, primary_key=True)
    matric_no = db.Column(String(20), unique=True, nullable=False)
    name = db.Column(String(120), nullable=False)
    department = db.Column(String(120), nullable=False)
    level = db.Column(String(10), nullable=False)
    user_id = db.Column(Integer, ForeignKey('user.id'), unique=True)
    temp_password = db.Column(String(128), nullable=True)
    results = relationship('Result', backref='student', lazy=True)
    # The `User.student_profile` relationship defines a backref named `user` on Student at runtime.
    # Provide a typing-only annotation so static checkers know `student.user` exists.
    if TYPE_CHECKING:  # pragma: no cover - typing only
        user: Optional["User"]

