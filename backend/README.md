# Infra Flow — Setup & Run Guide

## Prerequisites
- Python 3.8+
- MySQL 8.0+
- A browser (Chrome recommended)

---

## Step 1 — Database Setup

Open MySQL and run:

```sql
SOURCE /path/to/backend/database.sql;
```

Or paste the file contents directly into MySQL Workbench / phpMyAdmin.

This creates the `campusinfra_db` database, all tables, and inserts seed data (locations, technicians, sample issues).

---

## Step 2 — Configure Database Password

Open `backend/config.py` and set your MySQL root password:

```python
MYSQL_PASSWORD = 'yourpassword'   # ← change this
```

---

## Step 3 — Install Python Dependencies

```bash
cd backend
pip install Flask flask-mysqldb flask-cors bcrypt
```

---

## Step 4 — Run the Flask Backend

```bash
cd backend
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

Test it: open http://localhost:5000 in browser — should show `{"message": "Infra Flow backend running ✅"}`

---

## Step 5 — Open the Frontend

Open `frontend/front.html` directly in your browser (double-click or drag into browser).

No additional server needed for the frontend.

---

## Demo Flow for Examiner

| Step | Page | What it shows |
|------|------|---------------|
| 1 | `front.html` | Landing page |
| 2 | `register.html` | Register a new user → stored in `User` table |
| 3 | `login.html` | Login → Faculty/Staff go to Admin Dashboard, Students go to View Issues |
| 4 | `report_issue.html` | Submit an issue → written to `Issue` + `Reports` tables |
| 5 | `view_issues.html` | Lists all issues from DB live |
| 6 | `admin_dashboard.html` | Stats + filter by status, pulls from `dashboard/status-count` |
| 7 | `assign_technician.html` | Assign technician → creates `Slot`, `Has`, `Scheduled_In` records |
| 8 | `update_status.html` | Update issue status → updates `Issue.status` in DB |

---

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Register a new user |
| POST | `/login` | Login, returns role + user_id |
| GET | `/issues` | Get all issues |
| POST | `/issues` | Create a new issue |
| PUT | `/issues/update-status/<id>` | Update issue status |
| POST | `/issues/assign` | Assign technician to issue |
| GET | `/technicians` | Get all technicians |
| GET | `/dashboard/total-issues` | Count of all issues |
| GET | `/dashboard/status-count` | Issues grouped by status |
| GET | `/dashboard/category-count` | Issues grouped by category |
| GET | `/dashboard/user/<user_id>` | Issues reported by a specific user |

---

## Bug Fixes Applied

| File | Bug | Fix |
|------|-----|-----|
| `routes/issues.py` | Was a copy of auth.py with wrong blueprint name | Rewritten with proper issue routes |
| `routes/dashboard.py` | Used `issue_bp` instead of `dashboard_bp` in two routes | Fixed blueprint references |
| `utils/auth_utils.py` | Had a stray route definition inside it | Removed, kept only the decorator |
| `database.sql` | `User` table missing `password` column | Added `password VARCHAR(255)` |
| `config.py` | DB name was `college_maintenance`, didn't match SQL | Fixed to `campusinfra_db` |
| `report_issue.html` | JS referenced commented-out `priority` field, causing crash | Removed stale reference |
| `register.html` | Form had no IDs, no JS, no API call | Fully rewritten with API integration |
| All frontend forms | No API calls — purely static | All wired to Flask backend |
