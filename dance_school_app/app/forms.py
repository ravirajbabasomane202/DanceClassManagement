from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, BooleanField, DateField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from app.models import Staff, Student, Batch, StudentBatch
from datetime import datetime

class LoginForm(FlaskForm):
    """Form for user login (admin, staff, student)."""
    username = StringField('Username', validators=[DataRequired(message="Username is required.")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required.")])
    submit = SubmitField('Login')

class StudentRegistrationForm(FlaskForm):
    """Form for registering a new student (by admin or staff)."""
    full_name = StringField('Full Name', validators=[DataRequired(message="Full name is required.")])
    age = IntegerField('Age', validators=[DataRequired(message="Age is required.")])
    contact_number = StringField('Contact Number', validators=[Optional()])
    address = StringField('Address', validators=[Optional()])
    guardian_name = StringField('Guardian Name (if minor)', validators=[Optional()])
    email = StringField('Email', validators=[DataRequired(message="Email is required."), Email()])
    emergency_contact = StringField('Emergency Contact', validators=[Optional()])
    class_type = SelectField('Class Type', choices=[
        ('Hip-Hop', 'Hip-Hop'),
        ('Salsa', 'Salsa'),
        ('Classical', 'Classical')
    ], validators=[DataRequired(message="Please select a class type.")])
    submit = SubmitField('Register Student')

class StaffRegistrationForm(FlaskForm):
    """Form for registering a new staff member (by admin only)."""
    name = StringField('Name', validators=[DataRequired(message="Name is required.")])
    email = StringField('Email', validators=[DataRequired(message="Email is required."), Email()])
    phone = StringField('Phone', validators=[Optional()])
    specialization = StringField('Specialization', validators=[Optional()])
    salary = FloatField('Salary', validators=[Optional()])
    username = StringField('Username', validators=[DataRequired(message="Username is required."), Length(min=4, max=64)])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=6, message="Password must be at least 6 characters.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm the password."),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Register Staff')

class BatchForm(FlaskForm):
    """Form for creating a new batch (by admin only)."""
    name = StringField('Batch Name', validators=[DataRequired(message="Batch name is required.")])
    staff_id = SelectField('Assigned Staff', coerce=int, validators=[DataRequired(message="Please select a staff member.")])
    fee_monthly = FloatField('Monthly Fee', validators=[DataRequired(message="Monthly fee is required.")])
    fee_quarterly = FloatField('Quarterly Fee', validators=[Optional()])
    submit = SubmitField('Create Batch')

    def __init__(self, *args, **kwargs):
        super(BatchForm, self).__init__(*args, **kwargs)
        self.staff_id.choices = [(s.id, s.name) for s in Staff.query.order_by(Staff.name).all()]

class AssignStudentForm(FlaskForm):
    """Form for assigning a student to a batch (by admin or staff)."""
    student_id = SelectField('Student', coerce=int, validators=[DataRequired(message="Please select a student.")])
    submit = SubmitField('Assign Student')

    def __init__(self, *args, **kwargs):
        super(AssignStudentForm, self).__init__(*args, **kwargs)
        self.student_id.choices = [(s.id, s.full_name) for s in Student.query.order_by(Student.full_name).all()]

class AttendanceForm(FlaskForm):
    """Form for marking attendance for a student in a batch (by admin or staff)."""
    present = BooleanField('Present')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Mark Attendance')

class PaymentForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    batch_id = SelectField('Batch', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired()])
    due_date = DateField('Due Date', default=datetime.utcnow, validators=[Optional()])
    status = SelectField('Status', choices=[
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial')
    ], validators=[DataRequired()])
    submit = SubmitField('Update Payment')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_id.choices = [(s.id, s.full_name) for s in Student.query.all()]
        self.batch_id.choices = [(b.id, b.name) for b in Batch.query.all()]

class PublicStudentRegistrationForm(FlaskForm):
    """Form for public student registration (includes password)."""
    full_name = StringField('Full Name', validators=[DataRequired(message="Full name is required.")])
    age = IntegerField('Age', validators=[DataRequired(message="Age is required.")])
    contact_number = StringField('Contact Number', validators=[Optional()])
    address = StringField('Address', validators=[Optional()])
    guardian_name = StringField('Guardian Name (if minor)', validators=[Optional()])
    email = StringField('Email', validators=[DataRequired(message="Email is required."), Email()])
    emergency_contact = StringField('Emergency Contact', validators=[Optional()])
    class_type = SelectField('Class Type', choices=[
        ('Hip-Hop', 'Hip-Hop'),
        ('Salsa', 'Salsa'),
        ('Classical', 'Classical')
    ], validators=[DataRequired(message="Please select a class type.")])
    
    # Add password fields for public registration
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=6, message="Password must be at least 6 characters.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm the password."),
        EqualTo('password', message="Passwords must match.")
    ])
    submit = SubmitField('Register')