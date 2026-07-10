from ..extensions import db


class AcademicSession(db.Model):
    __tablename__ = 'academic_session'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
