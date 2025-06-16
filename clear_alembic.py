from sqlalchemy import text
from src.database.config import engine

def reset_alembic_and_enums():
    with engine.begin() as conn:
        # Drop alembic_version table if exists
        print("Menghapus tabel 'alembic_version' jika ada...")
        conn.execute(text("DROP TABLE IF EXISTS alembic_version"))

        # Drop all PostgreSQL ENUM types
        print("Mencari dan menghapus semua ENUM types...")
        enum_query = """
            SELECT n.nspname AS enum_schema, t.typname AS enum_name
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
            GROUP BY enum_schema, enum_name;
        """
        result = conn.execute(text(enum_query))
        enums = result.fetchall()

        for enum_schema, enum_name in enums:
            drop_enum = f'DROP TYPE IF EXISTS "{enum_schema}"."{enum_name}" CASCADE;'
            print(f"Menghapus ENUM: {enum_schema}.{enum_name}")
            conn.execute(text(drop_enum))

    print("✅ Reset selesai. Kamu bisa menjalankan `alembic upgrade head` lagi.")

if __name__ == "__main__":
    reset_alembic_and_enums()
