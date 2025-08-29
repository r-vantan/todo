import aiosqlite
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user INTEGER NOT NULL,
            name TEXT NOT NULL,
            color TEXT,
            FOREIGN KEY(user) REFERENCES users(id)
        );
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user INTEGER NOT NULL,
            shared_with TEXT,
            is_done INTEGER DEFAULT 0,
            name TEXT NOT NULL,
            description TEXT,
            tag INTEGER,
            deadline DATETIME,
            priority INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME,
            completed_at DATETIME,
            FOREIGN KEY(user) REFERENCES users(id),
            FOREIGN KEY(tag) REFERENCES tags(id)
        );
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS task_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(task_id) REFERENCES tasks(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
        await db.commit()

if __name__ == "__main__":
    asyncio.run(init_db())