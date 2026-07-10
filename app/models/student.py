from ..extensions import db
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship


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
    # No user relationship - use User.student_profile bidirectional

