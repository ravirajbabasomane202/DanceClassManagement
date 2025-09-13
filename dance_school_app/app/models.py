from app import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    """Base user model for authentication and role-based access."""
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'staff', 'student'
    active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationships
    student = db.relationship('Student', backref='user', uselist=False, lazy='joined')
    staff = db.relationship('Staff', backref='user', uselist=False, lazy='joined')

    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))

class Student(db.Model):
    """Model for student details."""
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    contact_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    guardian_name = db.Column(db.String(100))
    emergency_contact = db.Column(db.String(20))
    class_type = db.Column(db.String(50), nullable=False)  # e.g., 'Hip-Hop', 'Salsa'
    registration_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # profile_picture = db.Column(db.String(200))  # Path to uploaded image, optional

    # Relationships
    batches = db.relationship('Batch', secondary='student_batch', backref='students')

    def __repr__(self):
        return f'<Student {self.full_name} ({self.class_type})>'

class Staff(db.Model):
    """Model for staff details."""
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    specialization = db.Column(db.String(50))  # e.g., 'Hip-Hop Instructor'
    joining_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    salary = db.Column(db.Float)

    # Relationships
    batches = db.relationship('Batch', backref='staff', lazy='dynamic')

    def __repr__(self):
        return f'<Staff {self.name} ({self.specialization})>'

class Batch(db.Model):
    """Model for dance batches (e.g., Morning Salsa)."""
    __tablename__ = 'batch'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)  # e.g., 'Morning Salsa'
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    fee_monthly = db.Column(db.Float, nullable=False)
    fee_quarterly = db.Column(db.Float)

    def __repr__(self):
        return f'<Batch {self.name}>'

class StudentBatch(db.Model):
    """Many-to-many relationship between Student and Batch."""
    __tablename__ = 'student_batch'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)

    # Unique constraint to prevent duplicate assignments
    __table_args__ = (db.UniqueConstraint('student_id', 'batch_id', name='uix_student_batch'),)

    def __repr__(self):
        return f'<StudentBatch student_id={self.student_id}, batch_id={self.batch_id}>'

class Attendance(db.Model):
    """Model for tracking student attendance in a batch."""
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    present = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text)

    # Relationships
    student = db.relationship('Student', backref='attendances')
    batch = db.relationship('Batch', backref='attendances')

    # Unique constraint to prevent multiple attendance records for the same student/batch/date
    __table_args__ = (db.UniqueConstraint('student_id', 'batch_id', 'date', name='uix_attendance'),)

    def __repr__(self):
        return f'<Attendance student_id={self.student_id}, batch_id={self.batch_id}, date={self.date}>'

class Payment(db.Model):
    """Model for tracking student payments for a batch."""
    __tablename__ = 'payment'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    paid_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='unpaid', nullable=False)  # 'paid', 'unpaid', 'partial'

    # Relationships
    student = db.relationship('Student', backref='payments')
    batch = db.relationship('Batch', backref='payments')

    def __repr__(self):
        return f'<Payment student_id={self.student_id}, batch_id={self.batch_id}, status={self.status}>'