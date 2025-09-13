from app import create_app, db
from app.models import User, Staff, Student

# This creates an application context without running the server
app = create_app()

def add_users():
    """Adds test admin, staff, and student users to the database."""
    with app.app_context():
        print("Creating an admin user...")
        # Check if admin user already exists to avoid duplicates
        if User.query.filter_by(username='admin').first():
            print("Admin user already exists. Skipping...")
        else:
            admin_user = User(username='admin', email='admin@danceschool.com', role='admin')
            admin_user.set_password('password')  # Set a secure password for the admin
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Admin user created successfully.")

        print("\nCreating a staff user...")
        # Check if staff user already exists
        if User.query.filter_by(username='staff_user').first():
            print("Staff user already exists. Skipping...")
        else:
            staff_user = User(username='staff_user', email='staff@danceschool.com', role='staff')
            staff_user.set_password('password')  # Set a secure password
            db.session.add(staff_user)
            db.session.commit()
            # Link the new User to a Staff record
            staff = Staff(user_id=staff_user.id, name='Test Staff', phone='1234567890', specialization='Hip-Hop')
            db.session.add(staff)
            db.session.commit()
            print("✅ Staff user and linked Staff record created successfully.")

        print("\nCreating a student user...")
        # Check if student user already exists
        if User.query.filter_by(username='student_user').first():
            print("Student user already exists. Skipping...")
        else:
            student_user = User(username='student_user', email='student@danceschool.com', role='student')
            student_user.set_password('password')  # Set a secure password
            db.session.add(student_user)
            db.session.commit()
            # Link the new User to a Student record
            student = Student(user_id=student_user.id, full_name='Test Student', age=18, class_type='Salsa')
            db.session.add(student)
            db.session.commit()
            print("✅ Student user and linked Student record created successfully.")

if __name__ == '__main__':
    add_users()