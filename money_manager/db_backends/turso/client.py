from django.db.backends.sqlite3.client import DatabaseClient as SQLiteDatabaseClient

class DatabaseClient(SQLiteDatabaseClient):
    # Heredar el cliente de SQLite
    pass
