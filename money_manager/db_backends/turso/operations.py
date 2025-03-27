from django.db.backends.sqlite3.operations import DatabaseOperations as SQLiteDatabaseOperations

class DatabaseOperations(SQLiteDatabaseOperations):
    # Heredar todas las operaciones de SQLite
    pass
