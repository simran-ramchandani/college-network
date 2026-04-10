"""
database.py — SQLAlchemy engine + session factory
Edit DB_URL below to match your MySQL credentials.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
load_dotenv()

# ── Connection ────────────────────────────────────────────────
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT")
DB_NAME     = os.getenv("DB_NAME")

DB_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine       = create_engine(DB_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base         = declarative_base()


def get_db():
    """Yield a session, always close after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Connected successfully"
    except Exception as e:
        return False, str(e)


def ensure_schema_updates():
    """Apply small backward-compatible schema updates for existing databases."""
    with engine.begin() as conn:
        member_status_exists = conn.execute(text("""
            SELECT COUNT(*) AS count
            FROM information_schema.columns
            WHERE table_schema = :db_name
              AND table_name = 'club_memberships'
              AND column_name = 'member_status'
        """), {"db_name": DB_NAME}).scalar()

        if not member_status_exists:
            conn.execute(text("""
                ALTER TABLE club_memberships
                ADD COLUMN member_status
                ENUM('active', 'passed_out')
                DEFAULT 'active'
                AFTER role
            """))
