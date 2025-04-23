import sqlite3
from pathlib import Path
import sys
import os
# 数据库操作类，用于管理宠物的信息，包括添加、删除、查询等操作。
# 该类使用 SQLite 数据库来存储宠物的信息，包括名称、帧目录等。
# 该类的作用是提供一个统一的接口，用于操作宠物的信息，方便其他模块调用。
# 该类的方法包括：  
#   - init_db: 初始化数据库，创建 pets 表。
#   - add_pet: 添加宠物信息，包括名称和帧目录。
#   - delete_pet: 删除宠物信息，根据名称删除。
#   - get_all_pets: 获取所有宠物信息，返回一个字典，键为名称，值为帧目录。
#   - get_pet: 获取指定名称的宠物信息，返回帧目录。
#   - update_pet: 更新宠物信息，根据名称更新帧目录。        
class PetDB:
    def __init__(self):
        # 修改为使用绝对路径或打包后的相对路径
        if getattr(sys, 'frozen', False):
            self.db_path = os.path.join(sys._MEIPASS, 'pets.db')
        else:
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