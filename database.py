import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("community_tracker.db")

SAMPLE_PROJECTS = [
    ("Clean Water for Villages", "Water & Sanitation", "Andhra Pradesh",
     "Improve access to safe drinking water through community water points.", 72, 1200000, 850000, "In Progress"),
    ("Learning for Every Child", "Education", "Telangana",
     "Support learning materials and after-school mentoring for children.", 48, 900000, 410000, "In Progress"),
    ("Healthy Communities", "Healthcare", "Karnataka",
     "Organise community health screening and awareness camps.", 90, 650000, 620000, "Near Completion"),
    ("Green Neighbourhoods", "Environment", "Tamil Nadu",
     "Plant and maintain native trees with local volunteer groups.", 35, 500000, 160000, "In Progress"),
    ("Skills for Tomorrow", "Livelihoods", "Maharashtra",
     "Provide practical job-readiness and digital skills workshops.", 15, 750000, 90000, "Planning"),
]

PROJECT_IMAGE_URLS = {
    "Skills for Tomorrow": "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiNKJ2ZrTojsn7IezJXrCCvsywni8ZA5XkFwoFxLAfBSA42JFO9fIsYv84vf-oYnWiPRnfc_MHCmhL3gG6jyVvMdHowYnJBebROI1D1yEFW5YTy2m-9HRwUlCyksxU1D3AQIk1M17dxT24BCLhCJaVcci-fR9luorFl0VXO3nOTNNMwaiEpMy1XRaqvRZs/s1600-rw/pm-skills-of-tomorrow-program-2026-free-digital-and-ai-skills-training-by-navttc-apply-now.png",
    "Green Neighbourhoods": "https://tse3.mm.bing.net/th/id/OIP.oML-IX031Qkhq6kdpHTkYAHaE7?r=0&rs=1&pid=ImgDetMain&o=7&rm=3",
    "Healthy Communities": "https://www.centre4activeliving.ca/wp-content/uploads/2024/10/community-health-goals-unity.jpeg",
    "Learning for Every Child": "https://www.unicef.org/ethiopia/sites/unicef.org.ethiopia/files/styles/medium/public/publication/cover_image/Capture%20ECL%20cover.JPG.webp?itok=cwtZ3Z3S",
    "Clean Water for Villages": "https://storage.googleapis.com/wp-static-staging/wp_globalehsan_pillar/upload/img_cache/file-4204-657293e7e73a5da488e09450fc0cc7e0.jpg",
}

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    with connect() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, category TEXT NOT NULL, location TEXT NOT NULL,
            description TEXT NOT NULL, progress INTEGER NOT NULL DEFAULT 0,
            budget REAL NOT NULL DEFAULT 0, raised REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Planning',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        project_columns = {
            column["name"] for column in conn.execute("PRAGMA table_info(projects)")
        }
        if "image_url" not in project_columns:
            conn.execute("ALTER TABLE projects ADD COLUMN image_url TEXT")
        if conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 0:
            conn.executemany("""INSERT INTO projects
                (name, category, location, description, progress, budget, raised, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", SAMPLE_PROJECTS)
        conn.executemany(
            """UPDATE projects SET image_url = ?
               WHERE name = ? AND (image_url IS NULL OR image_url = '')""",
            ((url, name) for name, url in PROJECT_IMAGE_URLS.items()),
        )

def get_user_by_email(email):
    with connect() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

def create_user(email, password_hash):
    try:
        with connect() as conn:
            conn.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email, password_hash),
            )
    except sqlite3.IntegrityError:
        return False
    return True

def get_projects(search="", category="All categories"):
    search_like = f"%{search}%"
    sql = """SELECT * FROM projects
             WHERE (name LIKE ? OR location LIKE ? OR description LIKE ?)"""
    params = [search_like, search_like, search_like]
    if category != "All categories":
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY id DESC"
    with connect() as conn:
        return conn.execute(sql, params).fetchall()

def get_project(project_id):
    with connect() as conn:
        return conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()

def get_summary():
    with connect() as conn:
        row = conn.execute("""SELECT COUNT(*) AS projects,
            COALESCE(AVG(progress), 0) AS avg_progress,
            COALESCE(SUM(budget), 0) AS budget,
            COALESCE(SUM(raised), 0) AS raised FROM projects""").fetchone()
        return dict(row)

def add_project(values):
    with connect() as conn:
        conn.execute("""INSERT INTO projects
            (name, category, location, description, progress, budget, raised, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", values)

def delete_project(project_id):
    with connect() as conn:
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
