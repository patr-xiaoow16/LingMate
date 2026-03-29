from __future__ import annotations

from sqlalchemy import inspect, text

from app.db.session import engine


def run_lightweight_migrations() -> None:
    inspector = inspect(engine)
    if "materials" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("materials")}
        with engine.begin() as conn:
            if "file_name" not in columns:
                conn.execute(text("ALTER TABLE materials ADD COLUMN file_name VARCHAR(255) NOT NULL DEFAULT ''"))
            if "mime_type" not in columns:
                conn.execute(text("ALTER TABLE materials ADD COLUMN mime_type VARCHAR(128) NOT NULL DEFAULT ''"))
