# Taskmaster

A simple Flask-based task management web app with categories, priorities, due dates, and basic stats. Data is stored in SQLite by default.

## Features
- Create, edit, toggle, and delete tasks
- Categorize tasks and set priorities (High, Medium, Low)
- Simple stats page with totals and breakdowns
- JSON API at `/api/tasks` with filters

## Tech Stack
- Python, Flask
- SQLAlchemy ORM (+ Flask-Migrate installed, optional to use)
- SQLite (default) or any SQLAlchemy-supported DB

## Project Structure
```
./taskmanager.py        # Flask app entrypoint
./templates/            # Jinja2 templates (HTML pages)
./requirements.txt      # Python dependencies
./instance/             # Instance config folder (ignored)
./venv/                 # Local virtual env (ignored)
```

## Getting Started

### Prerequisites
- Python 3.10+ (tested with 3.11)

### Setup
```bash
# Clone the repo
git clone https://github.com/lilkloud/taskmaster.git
cd taskmaster

# Create and activate a virtual environment (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Or on macOS/Linux
# python -m venv .venv
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
You can optionally create a `.env` file in the project root:
```
SECRET_KEY=change-me
# SQLALCHEMY_DATABASE_URI=sqlite:///taskmanager.db   # default already set in code
```

### Initialize the Database
The app currently auto-creates tables on first run using `db.create_all()`. If you prefer migrations later, you can initialize Flask-Migrate.

### Run the App
```bash
python taskmanager.py
```
Then open: http://127.0.0.1:5000/

## API
- `GET /api/tasks`
  - Query params:
    - `status`: `completed` | `pending`
    - `priority`: `High` | `Medium` | `Low`
    - `search`: substring matched in title/description

Example:
```
curl "http://127.0.0.1:5000/api/tasks?status=pending&priority=High&search=report"
```

## Development Tips
- For rapid iteration, keep `debug=True` in `taskmanager.py`. Avoid it in production.
- If switching away from SQLite, set `SQLALCHEMY_DATABASE_URI` in `.env` (e.g., to PostgreSQL) and consider enabling Flask-Migrate fully.

## CI
This repo includes a minimal GitHub Actions workflow that:
- Sets up Python
- Caches pip dependencies
- Installs requirements
- Runs a syntax check (`python -m compileall .`)

You can extend it with linting (flake8, black) and tests (pytest) as needed.

## License
Add your preferred license (e.g., MIT). If you want, I can add an MIT LICENSE file for you.
