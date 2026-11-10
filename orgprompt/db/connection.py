"""SQLite Database connection and transaction management."""

import os
import sqlite3
from pathlib import Path
from typing import Optional

DEFAULT_DB_FILENAME = "org_knowledge_base.db"


def get_default_db_path() -> Path:
    """Returns the default absolute database path."""
    env_path = os.environ.get("ORGPROMPT_DB_PATH")
    if env_path:
        return Path(env_path)
    # Default to data/ directory inside project root
    project_root = Path(__file__).resolve().parent.parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / DEFAULT_DB_FILENAME


DEFAULT_DB_PATH = str(get_default_db_path())


def get_connection(
    db_path: Optional[str | Path] = None, enable_foreign_keys: bool = True
) -> sqlite3.Connection:
    """Creates a configured SQLite database connection with WAL mode and foreign keys enabled."""
    if db_path is None:
        target_path = str(get_default_db_path())
    elif isinstance(db_path, Path):
        target_path = str(db_path)
    else:
        target_path = db_path

    if target_path != ":memory:":
        parent = Path(target_path).parent
        if parent:
            parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(target_path)

    if enable_foreign_keys:
        conn.execute("PRAGMA foreign_keys = ON;")
    if target_path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")

    return conn


def get_schema_sql() -> str:
    """Reads the schema.sql file bundled with the package."""
    schema_file = Path(__file__).resolve().parent / "schema.sql"
    return schema_file.read_text(encoding="utf-8")


def init_db(db_path: Optional[str | Path] = None) -> sqlite3.Connection:
    """Initializes the database schema and triggers."""
    conn = get_connection(db_path)
    schema_sql = get_schema_sql()
    conn.executescript(schema_sql)
    conn.commit()
    return conn
