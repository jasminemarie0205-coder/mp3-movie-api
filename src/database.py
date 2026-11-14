import sqlite3
from pathlib import Path


def get_connection(db_path):
    """return a fresh connection with rows accessible by col name"""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(db_path):
    """create the movie table if does not exist"""
    connection = get_connection(db_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY,
                title TEXT,
                release_year INTEGER,
                rating REAL,
                genre TEXT
            )
            """
        )
        connection.commit()
    finally:
        connection.close()