import os
import sqlite3
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "research_hub.db")


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            topic TEXT,
            description TEXT,
            language TEXT DEFAULT 'Arabic',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            authors TEXT,
            year INTEGER,
            source_name TEXT,
            source_url TEXT,
            source_type TEXT DEFAULT 'Manual',
            abstract TEXT,
            summary TEXT,
            keywords TEXT,
            notes TEXT,
            language TEXT DEFAULT 'English',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paper_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(paper_id) REFERENCES papers(id)
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            detail TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS research_gaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            topic TEXT,
            summary TEXT,
            research_gap TEXT,
            recommendations TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );

        CREATE TABLE IF NOT EXISTS literature_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        );
        """
    )

    project_count = conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    if project_count == 0:
        conn.execute(
            "INSERT INTO projects (name, topic, description, language) VALUES (?, ?, ?, ?)",
            (
                "Paper Research Hub",
                "General research topic",
                "Default project for literature review and thesis tracking.",
                "Arabic",
            ),
        )

    conn.commit()
    conn.close()


def create_project(name, topic="", description="", language="Arabic"):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO projects (name, topic, description, language) VALUES (?, ?, ?, ?)",
        (name, topic, description, language),
    )
    conn.commit()
    project_id = cursor.lastrowid
    conn.close()
    return project_id


def list_projects():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_default_project_id():
    conn = get_connection()
    row = conn.execute("SELECT id FROM projects ORDER BY created_at DESC LIMIT 1").fetchone()
    conn.close()
    return row["id"] if row else None


def add_paper(
    project_id,
    title,
    authors="",
    year=None,
    source_name="",
    source_url="",
    source_type="Manual",
    abstract="",
    summary="",
    keywords="",
    notes="",
    language="English",
):
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO papers (
            project_id, title, authors, year, source_name, source_url, source_type,
            abstract, summary, keywords, notes, language, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            title,
            authors,
            year,
            source_name,
            source_url,
            source_type,
            abstract,
            summary,
            keywords,
            notes,
            language,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ),
    )
    conn.commit()
    paper_id = cursor.lastrowid
    conn.close()
    return paper_id


def list_papers(project_id=None, query="", language="All", source_type="All"):
    conn = get_connection()
    sql = "SELECT * FROM papers WHERE 1=1"
    params = []

    if project_id is not None:
        sql += " AND project_id = ?"
        params.append(project_id)

    if query:
        sql += " AND (title LIKE ? OR authors LIKE ? OR abstract LIKE ? OR keywords LIKE ? OR summary LIKE ? OR notes LIKE ?)"
        pattern = f"%{query}%"
        params.extend([pattern, pattern, pattern, pattern, pattern, pattern])

    if language != "All":
        sql += " AND language = ?"
        params.append(language)

    if source_type != "All":
        sql += " AND source_type = ?"
        params.append(source_type)

    sql += " ORDER BY created_at DESC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_paper(paper_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def delete_paper(paper_id):
    conn = get_connection()
    conn.execute("DELETE FROM notes WHERE paper_id = ?", (paper_id,))
    conn.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
    conn.commit()
    conn.close()


def add_note(paper_id, content):
    if not content.strip():
        return None
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO notes (paper_id, content) VALUES (?, ?)",
        (paper_id, content.strip()),
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return note_id


def list_notes(paper_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM notes WHERE paper_id = ? ORDER BY created_at DESC",
        (paper_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_task(project_id, title, status="Open", detail=""):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tasks (project_id, title, status, detail) VALUES (?, ?, ?, ?)",
        (project_id, title, status, detail),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id


def list_tasks(project_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats(project_id):
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM papers WHERE project_id = ?", (project_id,)).fetchone()[0]
    latest = conn.execute(
        "SELECT title FROM papers WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
        (project_id,),
    ).fetchone()
    latest_title = latest[0] if latest else "No records yet"
    conn.close()
    return {
        "total": total,
        "latest": latest_title,
    }


def get_all_langs():
    return ["All", "Arabic", "English", "Other"]


def get_all_source_types():
    return ["All", "Manual", "arXiv", "Crossref", "Database", "Conference", "Journal"]


def add_research_gap(project_id, topic, summary, research_gap, recommendations):
    conn = get_connection()
    conn.execute(
        "INSERT INTO research_gaps (project_id, topic, summary, research_gap, recommendations) VALUES (?, ?, ?, ?, ?)",
        (project_id, topic, summary, research_gap, recommendations),
    )
    conn.commit()
    conn.close()


def list_research_gaps(project_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM research_gaps WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_review(project_id, title, content):
    conn = get_connection()
    conn.execute(
        "INSERT INTO literature_reviews (project_id, title, content) VALUES (?, ?, ?)",
        (project_id, title, content),
    )
    conn.commit()
    conn.close()


def list_reviews(project_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM literature_reviews WHERE project_id = ? ORDER BY created_at DESC",
        (project_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
