from ..extensions import db


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    title = db.Column(db.String(120), nullable=False)
    unit = db.Column(db.Float, nullable=False)
    semester = db.Column(db.String(6), nullable=False)
    level = db.Column(db.String(10), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    results = db.relationship('Result', backref='course', lazy=True)
