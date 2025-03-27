from django.db.backends.sqlite3.schema import DatabaseSchemaEditor as SQLiteDatabaseSchemaEditor

class DatabaseSchemaEditor(SQLiteDatabaseSchemaEditor):
    # Heredar el editor de esquema de SQLite
    pass
