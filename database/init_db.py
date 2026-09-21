import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = BASE_DIR / "database" / "tourism.db"

SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def initialize_database():

    connection = sqlite3.connect(DATABASE_PATH)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:

        schema = schema_file.read()

    connection.executescript(schema)

    connection.commit()

    connection.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    initialize_database()