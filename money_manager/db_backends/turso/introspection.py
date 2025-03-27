from django.db.backends.sqlite3.introspection import DatabaseIntrospection as SQLiteDatabaseIntrospection

class DatabaseIntrospection(SQLiteDatabaseIntrospection):
    # Heredar la introspección de SQLite
    pass
