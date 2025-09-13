import os

# Define project structure
structure = {
    "dance_school_app": {
        "app": {
            "__init__.py": "",
            "config.py": "",
            "models.py": "",
            "forms.py": "",
            "routes.py": "",
            "templates": {
                "base.html": "",
                "login.html": "",
                "admin_dashboard.html": "",
                "staff_dashboard.html": "",
                "student_dashboard.html": "",
                "register_student.html": "",
                "edit_student.html": "",
                "attendance.html": "",
                "payments.html": "",
                "reports.html": "",
            },
            "static": {
                "css": {
                    "custom.css": ""
                },
                "js": {
                    "custom.js": ""
                }
            },
        },
        "migrations": {},
        "run.py": "",
        "requirements.txt": "",
    }
}


def create_structure(base_path, struct):
    for name, content in struct.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)


if __name__ == "__main__":
    create_structure(".", structure)
    print("✅ Project structure created successfully!")
