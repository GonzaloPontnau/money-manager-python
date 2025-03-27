from django.db.backends.sqlite3.creation import DatabaseCreation as SQLiteDatabaseCreation

class DatabaseCreation(SQLiteDatabaseCreation):
    # Heredar la creación de SQLite
    pass
