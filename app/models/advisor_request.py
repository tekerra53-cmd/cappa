from datetime import datetime
from ..extensions import db


class AdvisorStudentListRequest(db.Model):
    __tablename__ = 'advisor_student_list_requests'

    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    advisor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    note = db.Column(db.String(200), nullable=True)
    csv_path = db.Column(db.String(255), nullable=True)
    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    responded_at = db.Column(db.DateTime, nullable=True)

    admin = db.relationship('User', foreign_keys=[admin_id], backref='advisor_list_requests')
    advisor = db.relationship('User', foreign_keys=[advisor_id], backref='advisor_list_requests_received')
