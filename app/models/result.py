from ..extensions import db


class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('academic_session.id'), nullable=False)
    semester = db.Column(db.String(6), nullable=False)
    attendance = db.Column(db.Float, nullable=False, default=0)
    assignment = db.Column(db.Float, nullable=False, default=0)
    test = db.Column(db.Float, nullable=False, default=0)
    exam = db.Column(db.Float, nullable=False, default=0)
    total = db.Column(db.Float, nullable=False, default=0)
    grade = db.Column(db.String(2), nullable=False)
    grade_point = db.Column(db.Float, nullable=False)
    is_approved = db.Column(db.Boolean, nullable=False, default=False)
    approval_status = db.Column(db.String(20), nullable=False, default='pending')
    rejection_reason = db.Column(db.String(255), nullable=True)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

    session = db.relationship('AcademicSession', backref='results')
    approver = db.relationship('User', foreign_keys=[approved_by])

    def __init__(self, **kwargs):
        ca_value = kwargs.pop('ca', None)
        if ca_value is not None:
            kwargs.setdefault('assignment', ca_value)
        super().__init__(**kwargs)

    def compute(self):
        attendance = float(self.attendance or 0)
        assignment = float(self.assignment or 0)
        test = float(self.test or 0)
        exam = float(self.exam or 0)
        self.total = round(attendance + assignment + test + exam, 2)
        t = self.total
        if t >= 70:
            self.grade = 'A'
            self.grade_point = 5.0
        elif t >= 60:
            self.grade = 'B'
            self.grade_point = 4.0
        elif t >= 50:
            self.grade = 'C'
            self.grade_point = 3.0
        elif t >= 45:
            self.grade = 'D'
            self.grade_point = 2.0
        elif t >= 40:
            self.grade = 'E'
            self.grade_point = 1.0
        else:
            self.grade = 'F'
            self.grade_point = 0.0
