from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, FloatField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, Optional


class UserCreateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('lecturer','Lecturer')], validators=[DataRequired()])
    submit = SubmitField('Create User')





class CourseForm(FlaskForm):
    code = StringField('Course Code', validators=[DataRequired(), Length(max=10)])
    title = StringField('Title', validators=[DataRequired(), Length(max=120)])
    unit = FloatField('Unit', validators=[DataRequired(), NumberRange(min=0.5, max=10)])
    semester = SelectField('Semester', choices=[('1','1'), ('2','2')], validators=[DataRequired()])
    level = StringField('Level', validators=[DataRequired(), Length(max=10)])
    lecturer_id = SelectField('Lecturer', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Course')


class AcademicSessionForm(FlaskForm):
    name = StringField('Session', validators=[DataRequired(), Length(max=30)])
    submit = SubmitField('Add Session')


class AdvisorAssignForm(FlaskForm):
    lecturer_id = SelectField('Lecturer', coerce=int, validators=[DataRequired()])
    level = StringField('Advisor Level', validators=[Optional(), Length(max=10)])
    submit = SubmitField('Set Advisor')


class AdvisorListRequestForm(FlaskForm):
    advisor_id = SelectField('Advisor', coerce=int, validators=[DataRequired()])
    note = StringField('Request Note', validators=[Optional(), Length(max=200)])
    submit = SubmitField('Request Student List')
