from talent import create_app, db
from sqlalchemy import text

app = create_app()

# Columns to ensure exist in each table
community_post_cols = [
    ("user_id", "INTEGER"),
    ("image_filename", "VARCHAR(255)"),
]

user_cols = [
    ("username", "VARCHAR(150)"),
    ("avatar", "VARCHAR(255)"),
]

def add_columns_if_missing(table_name, columns):
    with db.engine.connect() as conn:
        # Get existing columns
        result = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
        existing_cols = [col[1] for col in result]

        for col_name, col_type in columns:
            if col_name not in existing_cols:
                try:
                    conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};"))
                    print(f"Added column '{col_name}' to '{table_name}'")
                except Exception as e:
                    print(f"Failed to add column '{col_name}' to '{table_name}': {e}")
            else:
                print(f"Column '{col_name}' already exists in '{table_name}'")

if __name__ == "__main__":
    with app.app_context():
        add_columns_if_missing("community_post", community_post_cols)
        add_columns_if_missing("user", user_cols)

        # Optional: populate user_id in community_post from author_id if empty
        try:
            db.engine.execute(text("UPDATE community_post SET user_id = author_id WHERE user_id IS NULL;"))
            print("Populated community_post.user_id from author_id")
        except Exception as e:
            print("Failed to populate community_post.user_id:", e)

        print("Migration complete.")
