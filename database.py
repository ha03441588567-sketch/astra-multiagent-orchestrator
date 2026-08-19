"""
Astra AI Workforce Platform — Database Layer
Lightweight SQLite persistence (zero external DB needed to run/demo).
"""

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "astra.db")


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                business_id TEXT NOT NULL,
                niche TEXT,
                channel TEXT,
                sender TEXT,          -- 'customer' or 'agent'
                agent_name TEXT,
                message TEXT,
                intent TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT NOT NULL,
                niche TEXT,
                customer_name TEXT,
                customer_phone TEXT,
                customer_email TEXT,
                status TEXT DEFAULT 'new',
                notes TEXT,
                created_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT
            )
        """)
        conn.commit()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def log_message(conversation_id, business_id, niche, channel, sender, agent_name, message, intent=None):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO conversations
               (conversation_id, business_id, niche, channel, sender, agent_name, message, intent, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (conversation_id, business_id, niche, channel, sender, agent_name, message, intent,
             datetime.utcnow().isoformat())
        )
        conn.commit()


def create_lead(business_id, niche, name=None, phone=None, email=None, notes=None):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO leads (business_id, niche, customer_name, customer_phone, customer_email, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (business_id, niche, name, phone, email, notes, datetime.utcnow().isoformat())
        )
        conn.commit()
        return cur.lastrowid


def create_task(business_id, agent_name, description):
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO tasks (business_id, agent_name, description, created_at)
               VALUES (?, ?, ?, ?)""",
            (business_id, agent_name, description, datetime.utcnow().isoformat())
        )
        conn.commit()
        return cur.lastrowid


def get_leads(business_id=None, limit=100):
    with get_conn() as conn:
        if business_id:
            rows = conn.execute(
                "SELECT * FROM leads WHERE business_id = ? ORDER BY id DESC LIMIT ?",
                (business_id, limit)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM leads ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


def get_tasks(business_id=None, limit=100):
    with get_conn() as conn:
        if business_id:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE business_id = ? ORDER BY id DESC LIMIT ?",
                (business_id, limit)
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM tasks ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]


def get_conversation(conversation_id):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM conversations WHERE conversation_id = ? ORDER BY id ASC",
            (conversation_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_stats():
    with get_conn() as conn:
        total_leads = conn.execute("SELECT COUNT(*) c FROM leads").fetchone()["c"]
        total_conversations = conn.execute(
            "SELECT COUNT(DISTINCT conversation_id) c FROM conversations"
        ).fetchone()["c"]
        total_tasks = conn.execute("SELECT COUNT(*) c FROM tasks").fetchone()["c"]
        pending_tasks = conn.execute(
            "SELECT COUNT(*) c FROM tasks WHERE status = 'pending'"
        ).fetchone()["c"]
        return {
            "total_leads": total_leads,
            "total_conversations": total_conversations,
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
        }
