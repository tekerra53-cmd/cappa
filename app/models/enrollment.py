from ..extensions import db


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True, autoincrement=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True, autoincrement=False)

    def __init__(self, student_id, course_id):
        self.student_id = student_id
        self.course_id = course_id
