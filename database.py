"""
database.py — Simple SQLite database management for AI Recruitment System.
Designed for student projects: uses standard Python sqlite3 with easy helper functions.
"""

import sqlite3
import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "ai_recruitment.db")


def get_db_connection():
    """Establishes and returns a SQLite database connection with row factory."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if existing candidates table has education column, if not reset
    cursor.execute("PRAGMA table_info(candidates)")
    cols = [row["name"] for row in cursor.fetchall()]
    if cols and "education" not in cols:
        cursor.execute("DROP TABLE IF EXISTS candidates")
        cursor.execute("DROP TABLE IF EXISTS interviews")
        cursor.execute("DROP TABLE IF EXISTS email_logs")

    # Table 1: Candidates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT DEFAULT 'Not Available',
            education TEXT DEFAULT 'Not Available',
            skills TEXT DEFAULT 'Not Available',
            experience TEXT DEFAULT 'Not Available',
            certifications TEXT DEFAULT 'Not Available',
            cv_filename TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table 2: Interviews
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            questions_json TEXT NOT NULL,
            answers_json TEXT DEFAULT '[]',
            score INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Pending',
            feedback TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
        )
    """)

    # Table 3: Email Logs (for Mock Email Mode)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER NOT NULL,
            email_type TEXT NOT NULL,
            recipient_email TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# Candidate Helper Functions
def create_candidate(data: dict) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO candidates (name, email, phone, education, skills, experience, certifications, cv_filename, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name", "Not Available"),
        data.get("email", "Not Available"),
        data.get("phone", "Not Available"),
        data.get("education", "Not Available"),
        data.get("skills", "Not Available"),
        data.get("experience", "Not Available"),
        data.get("certifications", "Not Available"),
        data.get("cv_filename", "uploaded_cv.pdf"),
        data.get("status", "Pending")
    ))
    conn.commit()
    candidate_id = cursor.lastrowid
    conn.close()
    return candidate_id


def get_all_candidates():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, 
               i.token as interview_token, 
               i.score as interview_score, 
               i.status as interview_status
        FROM candidates c
        LEFT JOIN interviews i ON c.id = i.candidate_id
        ORDER BY c.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_candidate_by_id(candidate_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_candidate_status(candidate_id: int, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET status = ? WHERE id = ?", (status, candidate_id))
    conn.commit()
    conn.close()


# Interview Helper Functions
def create_interview(candidate_id: int, token: str, questions: list) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interviews (candidate_id, token, questions_json, status)
        VALUES (?, ?, ?, 'Generated')
    """, (candidate_id, token, json.dumps(questions)))
    conn.commit()
    interview_id = cursor.lastrowid
    conn.close()
    return interview_id


def get_interview_by_token(token: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.*, c.name as candidate_name, c.email as candidate_email, c.skills as candidate_skills
        FROM interviews i
        JOIN candidates c ON i.candidate_id = c.id
        WHERE i.token = ?
    """, (token,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data["questions"] = json.loads(data["questions_json"])
        data["answers"] = json.loads(data["answers_json"]) if data["answers_json"] else []
        return data
    return None


def get_interview_by_candidate_id(candidate_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interviews WHERE candidate_id = ?", (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data["questions"] = json.loads(data["questions_json"])
        data["answers"] = json.loads(data["answers_json"]) if data["answers_json"] else []
        return data
    return None


def update_interview_submission(token: str, answers: list, score: int, status: str, feedback: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE interviews 
        SET answers_json = ?, score = ?, status = ?, feedback = ?, submitted_at = CURRENT_TIMESTAMP
        WHERE token = ?
    """, (json.dumps(answers), score, status, feedback, token))
    conn.commit()
    conn.close()


# Email Helper Functions
def log_email(candidate_id: int, email_type: str, recipient_email: str, subject: str, body: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO email_logs (candidate_id, email_type, recipient_email, subject, body)
        VALUES (?, ?, ?, ?, ?)
    """, (candidate_id, email_type, recipient_email, subject, body))
    conn.commit()
    conn.close()


def get_all_email_logs():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM email_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
