from datetime import datetime
from ..extensions import db


class ResultApprovalHistory(db.Model):
    __tablename__ = 'result_approval_history'

    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    note = db.Column(db.String(255), nullable=True)
    acted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    acted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    result = db.relationship('Result', backref='approval_history')
    actor = db.relationship('User', foreign_keys=[acted_by])
