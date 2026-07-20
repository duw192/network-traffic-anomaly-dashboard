"""Compatibility exports for the Day 11 database module contract."""

from backend.app.db.database import get_connection, get_database_path, initialize_database, session_scope

__all__ = ["get_connection", "get_database_path", "initialize_database", "session_scope"]
