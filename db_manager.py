import sqlite3
from pathlib import Path

class PetDB:
    def __init__(self):
        self.db_path = "pets.db"
        self.init_db()
        
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    frames_dir TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
    def add_pet(self, name, frames_dir):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO pets (name, frames_dir) VALUES (?, ?)",
                (name, frames_dir)
            )
            conn.commit()
            
    def delete_pet(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM pets WHERE name = ?", (name,))
            conn.commit()
            
    def get_all_pets(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, frames_dir FROM pets")
            return {row[0]: row[1] for row in cursor.fetchall()}

    def update_pet(self, old_name, new_name, new_frames_dir):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pets SET name = ?, frames_dir = ? WHERE name = ?",
                (new_name, new_frames_dir, old_name)
            )
            conn.commit()

    def get_pet(self, name):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT frames_dir FROM pets WHERE name = ?", (name,))
            result = cursor.fetchone()
            return result[0] if result else None