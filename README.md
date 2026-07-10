# Student Result Management System (SRMS)

## Overview
Full-stack MVP web app: Flask + SQLAlchemy + MySQL (or SQLite for dev) + Bootstrap + Jinja2.
Modular architecture with blueprints for auth, admin, lecturer, student modules.

## Features
- RBAC: admin, lecturer, student
- Admin: user/course/session/student management
- Lecturer: assign results by course; auto total/grade/gp
- Student: view results + GPA/CGPA, filter by session/semester
- Authentication: login/logout, password hashing
- Validation + flash messages
- Automated result computation with grade scaling

## Project Structure
```
app/
├── __init__.py              # App factory & extensions init
├── config.py               # Config settings (DB, secret key)
├── extensions.py           # SQLAlchemy, LoginManager, CSRF
├── models/                 # Database models
├── auth/                   # Authentication module
├── admin/                  # Admin module
├── lecturer/               # Lecturer module
├── student/                # Student module
├── core/                   # Shared logic (decorators, utils)
├── templates/              # Jinja2 templates
└── static/                 # CSS, JS, assets

tests/                      # Unit tests
seed.py                     # Fake data generator
run.py                      # App entry point
```

## Setup
1. Create virtualenv
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment (optional)
   Copy `.env` and modify as needed:
   ```bash
   cp .env .env.local
   # Edit DATABASE_URL, SECRET_KEY, etc.
   ```

4. Initialize database
   ```bash
   flask db init
   flask db migrate -m "init"
   flask db upgrade
   ```

5. Seed with fake data (optional)
   ```bash
   python seed.py
   ```

6. Run the application
   ```bash
   python run.py
   ```

## Default Credentials (after seeding)
- **Admin**: admin / admin123
- **Lecturers/Students**: Any generated username / pass123

## Endpoints
- `/` -> redirects based on role
- `/login`, `/logout`
- `/admin/dashboard`, `/admin/users`, `/admin/students`, `/admin/courses`, `/admin/sessions`
- `/lecturer/dashboard`, `/lecturer/course/<id>/results`
- `/student/dashboard`

## Testing
Run unit tests:
```bash
pytest
```

## Notes
- Uses SQLite by default, configure `DATABASE_URL` in `.env` for MySQL
- Change `SECRET_KEY` in `.env` for production
- MySQL support via `mysqlclient` dependency

## Extras
- Audit logs enabled in models
- Modular blueprint architecture
- Automated GPA/CGPA calculation
- Role-based route protection
- Optional features: PDF export, analytics, REST API are extensible
# cappa
