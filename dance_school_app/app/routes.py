from flask import render_template, redirect, url_for, flash, request, send_file, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required 
from app import db
from app.models import User, Student, Staff, Batch, Attendance, Payment, StudentBatch
from app.forms import LoginForm, StudentRegistrationForm, StaffRegistrationForm, AttendanceForm, PaymentForm , BatchForm, AssignStudentForm, PublicStudentRegistrationForm
from sqlalchemy import func
from io import BytesIO
import pandas as pd
from datetime import datetime, date, timedelta
from flask import Blueprint
import os

# Blueprint for better organization
bp = Blueprint('main', __name__)

def role_required(roles):
    """Decorator to restrict access to specific roles."""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash('Access denied.', 'danger')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
# Authentication Routes
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.active:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

# Dashboard Redirect Based on Role
@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('main.admin_dashboard'))
    elif current_user.role == 'staff':
        return redirect(url_for('main.staff_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('main.student_dashboard'))
    return 'Invalid role', 403

# Admin Routes
@bp.route('/admin/dashboard')
@login_required
@role_required(['admin'])
def admin_dashboard():
    total_students = Student.query.count()
    total_staff = Staff.query.count()
    total_batches = Batch.query.count()
    unpaid_payments = Payment.query.filter_by(status='unpaid').count()

    # Chart Data: Students by Class Type
    students_by_class = db.session.query(Student.class_type, func.count(Student.id)) \
        .group_by(Student.class_type).all()
    class_labels = [row[0] for row in students_by_class]
    class_counts = [row[1] for row in students_by_class]

    # Chart Data: Payments by Status
    payments_status = db.session.query(Payment.status, func.count(Payment.id)) \
        .group_by(Payment.status).all()
    status_labels = [row[0] for row in payments_status]
    status_counts = [row[1] for row in payments_status]

    return render_template('admin_dashboard.html', 
                         total_students=total_students, 
                         total_staff=total_staff, 
                         total_batches=total_batches, 
                         unpaid_payments=unpaid_payments,
                         class_labels=class_labels, class_counts=class_counts,
                         status_labels=status_labels, status_counts=status_counts)

@bp.route('/admin/staff/register', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def register_staff():
    form = StaffRegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first() or User.query.filter_by(email=form.email.data).first():
            flash('Username or email already exists.', 'danger')
            return render_template('register_staff.html', form=form)
        user = User(username=form.username.data, email=form.email.data, role='staff')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        staff = Staff(user_id=user.id, name=form.name.data, phone=form.phone.data, 
                      specialization=form.specialization.data, salary=form.salary.data)
        db.session.add(staff)
        db.session.commit()
        flash('Staff registered successfully.', 'success')
        return redirect(url_for('main.admin_dashboard'))
    return render_template('register_staff.html', form=form)

@bp.route('/admin/staff/list')
@login_required
def staff_list():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    staff_members = Staff.query.all()
    return render_template('staff_list.html', staff_members=staff_members)

# Student Routes
@bp.route('/student/register', methods=['GET', 'POST'])
@login_required
def register_student():
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('register_student.html', form=form)
        
        # Generate username from email and ensure it's unique
        username = form.email.data.split('@')[0]
        counter = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1
            
        user = User(username=username, email=form.email.data, role='student')
        user.set_password('defaultpass')  # TODO: Generate random or send via email
        db.session.add(user)
        db.session.commit()
        student = Student(user_id=user.id, full_name=form.full_name.data, age=form.age.data, 
                         contact_number=form.contact_number.data, address=form.address.data, 
                         guardian_name=form.guardian_name.data, emergency_contact=form.emergency_contact.data, 
                         class_type=form.class_type.data)
        db.session.add(student)
        db.session.commit()
        flash('Student registered successfully.', 'success')
        return redirect(url_for('main.student_list'))
    return render_template('register_student.html', form=form)

@bp.route('/student/list')
@login_required
@role_required(['admin', 'staff'])
def student_list():
    students = Student.query.filter_by().all()
    return render_template('student_list.html', students=students)

@bp.route('/student/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'staff'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    form = StudentRegistrationForm(obj=student)
    if form.validate_on_submit():
        student.full_name = form.full_name.data
        student.age = form.age.data
        student.contact_number = form.contact_number.data
        student.address = form.address.data
        student.guardian_name = form.guardian_name.data
        student.emergency_contact = form.emergency_contact.data
        student.class_type = form.class_type.data
        student.user.email = form.email.data
        db.session.commit()
        flash('Student updated successfully.', 'success')
        return redirect(url_for('main.student_list'))
    return render_template('edit_student.html', form=form, student=student)

@bp.route('/student/delete/<int:student_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    user = student.user
    user.active = False
    db.session.commit()
    flash('Student deactivated.', 'success')
    return redirect(url_for('main.student_list'))

# Staff Dashboard
@bp.route('/staff/dashboard')
@login_required
@role_required(['staff'])
def staff_dashboard():
    staff = current_user.staff
    assigned_batches = Batch.query.filter_by(staff_id=staff.id).all()

    # Get IDs of batches assigned to the staff
    assigned_batch_ids = [b.id for b in assigned_batches]

    # Summary card data
    total_batches = len(assigned_batches)
    # Count unique students across all assigned batches
    total_students = db.session.query(func.count(func.distinct(StudentBatch.student_id)))\
        .filter(StudentBatch.batch_id.in_(assigned_batch_ids)).scalar() or 0
    # Count unpaid payments for assigned batches
    unpaid_payments = Payment.query.filter(Payment.batch_id.in_(assigned_batch_ids), Payment.status == 'unpaid').count()

    # Chart Data: Students per Batch
    batch_student_counts = db.session.query(Batch.name, func.count(StudentBatch.student_id)) \
        .join(StudentBatch).filter(Batch.staff_id == staff.id).group_by(Batch.name).all()
    batch_labels = [row[0] for row in batch_student_counts]
    batch_counts = [row[1] for row in batch_student_counts]

    # Chart Data: Attendance Summary (Present vs Absent)
    attendance_summary = db.session.query(Attendance.present, func.count(Attendance.id)) \
        .join(Batch).filter(Batch.staff_id == staff.id).group_by(Attendance.present).all()
    attendance_labels = ['Present' if row[0] else 'Absent' for row in attendance_summary]
    attendance_counts = [row[1] for row in attendance_summary]

    return render_template('staff_dashboard.html', 
                           total_students=total_students, total_batches=total_batches, unpaid_payments=unpaid_payments,
                           batches=assigned_batches, 
                           batch_labels=batch_labels, batch_counts=batch_counts,
                           attendance_labels=attendance_labels, attendance_counts=attendance_counts)

# Batch Routes
@bp.route('/batch/create', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def create_batch():
    form = BatchForm()  # Assume a BatchForm with name, staff_id, fee_monthly, fee_quarterly
    form.staff_id.choices = [(s.id, s.name) for s in Staff.query.all()]
    if form.validate_on_submit():
        batch = Batch(name=form.name.data, staff_id=form.staff_id.data, 
                      fee_monthly=form.fee_monthly.data, fee_quarterly=form.fee_quarterly.data)
        db.session.add(batch)
        db.session.commit()
        flash('Batch created successfully.', 'success')
        return redirect(url_for('main.batch_list'))
    return render_template('create_batch.html', form=form)

@bp.route('/batch/list')
@login_required
@role_required(['admin', 'staff'])
def batch_list():
    batches = Batch.query.all()
    return render_template('batch_list.html', batches=batches)

@bp.route('/batch/assign_student/<int:batch_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'staff'])
def assign_student_to_batch(batch_id):
    batch = Batch.query.get_or_404(batch_id)
    form = AssignStudentForm()  # Assume form with student_id
    form.student_id.choices = [(s.id, s.full_name) for s in Student.query.all()]
    if form.validate_on_submit():
        student_batch = StudentBatch(student_id=form.student_id.data, batch_id=batch_id)
        db.session.add(student_batch)
        db.session.commit()
        flash('Student assigned to batch.', 'success')
        return redirect(url_for('main.batch_list'))
    return render_template('assign_student.html', form=form, batch=batch)

# Attendance Routes
@bp.route('/attendance/mark/<int:batch_id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'staff'])
def mark_attendance(batch_id):
    batch = Batch.query.get_or_404(batch_id)
    students = Student.query.join(StudentBatch).filter(StudentBatch.batch_id == batch_id).all()
    forms = {student.id: AttendanceForm(prefix=str(student.id)) for student in students}
    if request.method == 'POST':
        for student in students:
            form = forms[student.id]
            if form.validate_on_submit():
                attendance = Attendance(student_id=student.id, batch_id=batch_id, 
                                       date=datetime.utcnow().date(), 
                                       present=form.present.data, 
                                       notes=form.notes.data)
                db.session.add(attendance)
        db.session.commit()
        flash('Attendance marked successfully.', 'success')
        return redirect(url_for('main.batch_list'))
    return render_template('attendance.html', forms=forms, students=students, batch=batch)

# Payment Routes
@bp.route('/payment/update/<int:student_id>', methods=['GET', 'POST'])
@login_required
def update_payment(student_id):
    """Create or update a payment record."""
    if current_user.role not in ['admin', 'staff']:
        abort(403)

    payment_id = request.args.get('payment_id', type=int)
    payment = Payment.query.get_or_404(payment_id) if payment_id else None
    student = None

    if payment_id:
        student = payment.student
    elif student_id:
        student = Student.query.get_or_404(student_id)
    # If student_id is 0, this is a generic "add payment" page.

    batches = Batch.query.all()
    # Pass all students to the template for the dropdown if creating a new payment.
    all_students = Student.query.order_by(Student.full_name).all() if not student else None

    if request.method == 'POST':
        batch_id = request.form.get('batch_id', type=int)
        amount = request.form.get('amount', type=float)
        due_date_str = request.form.get('due_date')
        paid_date_str = request.form.get('paid_date')
        status = request.form.get('status')

        if not batch_id or not amount or not status:
            flash('Batch, Amount, and Status are required.', 'danger')
            return redirect(request.url)

        if payment:
            # Update existing payment
            payment.batch_id = batch_id
            payment.amount = amount
            payment.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None
            payment.paid_date = datetime.strptime(paid_date_str, '%Y-%m-%d').date() if paid_date_str else None
            payment.status = status
            flash('Payment updated successfully.', 'success')
        else:
            # Create new payment
            final_student_id = student.id if student else request.form.get('student_id', type=int)
            if not final_student_id:
                flash('Student is required for a new payment.', 'danger')
                return redirect(request.url)
            new_payment = Payment(
                student_id=final_student_id,
                batch_id=batch_id,
                amount=amount,
                due_date=datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None,
                paid_date=datetime.strptime(paid_date_str, '%Y-%m-%d').date() if paid_date_str else None,
                status=status
            )
            db.session.add(new_payment)
            flash('Payment created successfully.', 'success')

        db.session.commit()
        return redirect(url_for('main.payment_list'))

    return render_template('update_payment.html',
                         student=student,
                         batches=batches,
                         payment=payment,
                         students=all_students)

@bp.route('/payment/list')
@login_required
def payment_list():
    if current_user.role not in ['admin', 'staff']:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    payments = Payment.query.all()
    return render_template('payment_list.html', payments=payments)

# Student Dashboard
@bp.route('/student/dashboard')
@login_required
@role_required(['student'])
def student_dashboard():
    student = current_user.student
    attendances = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).all()
    payments = Payment.query.filter_by(student_id=student.id).all()
    batches = Batch.query.join(StudentBatch).filter(StudentBatch.student_id == student.id).all()

    # Summary card data
    total_batches = len(batches)
    unpaid_payments = Payment.query.filter_by(student_id=student.id, status='unpaid').count()
    
    # Chart Data: Attendance Over Last 30 Days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_attendances = Attendance.query.filter(Attendance.student_id == student.id, Attendance.date >= thirty_days_ago) \
        .order_by(Attendance.date).all()
    
    # For summary card
    recent_attendance = sum(1 for att in recent_attendances if att.present)
    
    # For chart
    attendance_dates = [att.date.strftime('%Y-%m-%d') for att in recent_attendances]
    attendance_status = [1 if att.present else 0 for att in recent_attendances]  # 1 for present, 0 for absent

    # Chart Data: Payments by Status
    student_payments_status = db.session.query(Payment.status, func.count(Payment.id)) \
        .filter(Payment.student_id == student.id).group_by(Payment.status).all()
    student_status_labels = [row[0] for row in student_payments_status]
    student_status_counts = [row[1] for row in student_payments_status]

    return render_template('student_dashboard.html', 
                           student=student, attendances=attendances, payments=payments, batches=batches,
                           total_batches=total_batches, unpaid_payments=unpaid_payments, recent_attendance=recent_attendance,
                           attendance_dates=attendance_dates, attendance_status=attendance_status,
                           student_status_labels=student_status_labels, student_status_counts=student_status_counts)

# Reports Export
@bp.route('/reports/students')
@login_required
@role_required(['admin'])
def export_students():
    students = Student.query.all()
    df = pd.DataFrame([{
        'ID': s.id,
        'Name': s.full_name,
        'Age': s.age,
        'Class': s.class_type,
        'Contact': s.contact_number,
        'Email': s.user.email
    } for s in students])
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='students_report.csv', as_attachment=True)

@bp.route('/reports/attendance')
@login_required
@role_required(['admin'])
def export_attendance():
    attendances = Attendance.query.all()
    df = pd.DataFrame([{
        'Student ID': a.student_id,
        'Student Name': a.student.full_name,
        'Batch': a.batch.name,
        'Date': a.date,
        'Present': 'Yes' if a.present else 'No',
        'Notes': a.notes
    } for a in attendances])
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(output, mimetype='text/csv', download_name='attendance_report.csv', as_attachment=True)

@bp.route('/register', methods=['GET', 'POST'])
def public_register():
    """Public registration page for students."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = PublicStudentRegistrationForm()
    if form.validate_on_submit():
        # Check if email already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html', form=form)
        
        # Generate username from email
        username = form.email.data.split('@')[0]
        # Check if username exists, append numbers if needed
        counter = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}{counter}"
            counter += 1
        
        user = User(username=username, email=form.email.data, role='student')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        student = Student(user_id=user.id, full_name=form.full_name.data, age=form.age.data,
                         contact_number=form.contact_number.data, address=form.address.data,
                         guardian_name=form.guardian_name.data, emergency_contact=form.emergency_contact.data,
                         class_type=form.class_type.data)
        db.session.add(student)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

@bp.route('/api/batches/<int:batch_id>')
@login_required
def get_batch_fee(batch_id):
    """Get fee information for a batch."""
    batch = Batch.query.get_or_404(batch_id)
    return jsonify({
        'fee_monthly': batch.fee_monthly,
        'fee_quarterly': batch.fee_quarterly
    })

@bp.route('/api/batches')
@login_required
def get_all_batches():
    """Get all batches."""
    batches = Batch.query.all()
    
    return jsonify({
        'batches': [{
            'id': batch.id,
            'name': batch.name,
            'fee_monthly': batch.fee_monthly,
            'fee_quarterly': batch.fee_quarterly
        } for batch in batches]
    })
