from datetime import datetime
from ..extensions import db


class AdvisorResultSubmission(db.Model):
    __tablename__ = 'advisor_result_submissions'

    id = db.Column(db.Integer, primary_key=True)
    advisor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    level = db.Column(db.String(10), nullable=False)
    department = db.Column(db.String(120), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('academic_session.id'), nullable=False)
    semester = db.Column(db.String(6), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='advisor_submitted')
    note = db.Column(db.String(255), nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    admin_approved_at = db.Column(db.DateTime, nullable=True)

    advisor = db.relationship('User', foreign_keys=[advisor_id])
    admin = db.relationship('User', foreign_keys=[admin_id])
    session = db.relationship('AcademicSession')
