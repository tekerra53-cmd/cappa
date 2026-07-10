from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, StringField
from wtforms.validators import DataRequired, NumberRange, Length, Email, Optional
from ..core.constants import ATTENDANCE_MAX, ASSIGNMENT_MAX, TEST_MAX, EXAM_MAX


class ResultEntryForm(FlaskForm):
    attendance = FloatField(
        f'Attendance (0 - {ATTENDANCE_MAX})',
        validators=[DataRequired(), NumberRange(min=0, max=ATTENDANCE_MAX)]
    )
    assignment = FloatField(
        f'Assignment (0 - {ASSIGNMENT_MAX})',
        validators=[DataRequired(), NumberRange(min=0, max=ASSIGNMENT_MAX)]
    )
    test = FloatField(
        f'Test (0 - {TEST_MAX})',
        validators=[DataRequired(), NumberRange(min=0, max=TEST_MAX)]
    )
    exam = FloatField(
        f'Exam (0 - {EXAM_MAX})',
        validators=[DataRequired(), NumberRange(min=0, max=EXAM_MAX)]
    )
    submit = SubmitField('Save')

class StudentCreateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    email = StringField('Email (optional)', validators=[Optional(), Email(), Length(max=120)])
    department = StringField('Department', validators=[DataRequired(), Length(max=120)])
    submit = SubmitField('Create Student')
