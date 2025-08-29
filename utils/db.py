import aiosqlite
import bcrypt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH

async def encryption(password):
    """
    パスワードをハッシュ化する
    
    Args:
        password (str): ハッシュ化するパスワード
        
    Returns:
        bytes: ハッシュ化されたパスワード
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

async def create_user(name, email, password):
    """
    新しいユーザーを作成する
    
    Args:
        name (str): ユーザー名
        email (str): メールアドレス
        password (str): パスワード（ハッシュ化前）
        
    Returns:
        None
    """
    hashed_password = await encryption(password)
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )
        await conn.commit()

async def get_user_by_email(email):
    """
    メールアドレスでユーザー情報を取得する
    
    Args:
        email (str): 検索するメールアドレス
        
    Returns:
        tuple or None: ユーザー情報のタプル（id, name, email, password）、見つからない場合はNone
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("SELECT * FROM users WHERE email = ?", (email,))
        return await cursor.fetchone()

async def verify_password(stored_password, provided_password):
    """
    パスワードを検証する
    
    Args:
        stored_password (bytes): ハッシュ化されて保存されているパスワード
        provided_password (str): 検証したいパスワード（平文）
        
    Returns:
        bool: パスワードが一致する場合True、一致しない場合False
    """
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

async def auth_user(email, password):
    """
    ユーザー認証を行う
    
    Args:
        email (str): ログインするメールアドレス
        password (str): ログインするパスワード（平文）
        
    Returns:
        tuple or False: 認証成功時はユーザー情報のタプル、失敗時はFalse
    """
    user = await get_user_by_email(email)
    if user and await verify_password(user[3], password):
        return user
    return False

async def create_tag(user_id, name, color=None):
    """
    新しいタグを作成する
    
    Args:
        user_id (int): タグを作成するユーザーのID
        name (str): タグ名
        color (str, optional): タグの色。デフォルトはNone
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO tags (user, name, color) VALUES (?, ?, ?)",
            (user_id, name, color)
        )
        await conn.commit()

async def get_tags_by_user(user_id):
    """
    指定ユーザーのタグ一覧を取得する
    
    Args:
        user_id (int): タグを取得するユーザーのID
        
    Returns:
        list: タグ情報のタプルのリスト
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("SELECT * FROM tags WHERE user = ?", (user_id,))
        return await cursor.fetchall()

async def create_task(user_id, name, description=None, tag=None, deadline=None, priority=0):
    """
    新しいタスクを作成する
    
    Args:
        user_id (int): タスクを作成するユーザーのID
        name (str): タスク名
        description (str, optional): タスクの詳細説明。デフォルトはNone
        tag (int, optional): タグID。デフォルトはNone
        deadline (datetime, optional): 締め切り日時。デフォルトはNone
        priority (int, optional): 優先度。デフォルトは0
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            """INSERT INTO tasks (user, name, description, tag, deadline, priority)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, name, description, tag, deadline, priority)
        )
        await conn.commit()

async def get_tasks_by_user(user_id):
    """
    指定ユーザーが作成したタスク一覧を取得する
    
    Args:
        user_id (int): タスクを取得するユーザーのID
        
    Returns:
        list: タスク情報のタプルのリスト
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("SELECT * FROM tasks WHERE user = ?", (user_id,))
        return await cursor.fetchall()

async def mark_task_done(task_id):
    """
    タスクを完了状態にする
    
    Args:
        task_id (int): 完了にするタスクのID
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE tasks SET is_done = 1, completed_at = CURRENT_TIMESTAMP WHERE id = ?",
            (task_id,)
        )
        await conn.commit()

async def share_task(task_id, user_ids):
    """
    タスクを複数ユーザーに共有する
    
    Args:
        task_id (int): 共有するタスクのID
        user_ids (list): 共有先ユーザーIDのリスト
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        for user_id in user_ids:
            await conn.execute(
                "INSERT INTO task_shares (task_id, user_id) VALUES (?, ?)",
                (task_id, user_id)
            )
        await conn.commit()

async def get_shared_tasks(user_id):
    """
    指定ユーザーが他ユーザーから共有されたタスク一覧を取得する
    
    Args:
        user_id (int): 共有されたタスクを取得するユーザーのID
        
    Returns:
        list: 共有されたタスク情報のタプルのリスト
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            """SELECT tasks.* FROM tasks
               JOIN task_shares ON tasks.id = task_shares.task_id
               WHERE task_shares.user_id = ?""",
            (user_id,)
        )
        return await cursor.fetchall()

async def get_shared_tasks_by_user(user_id):
    """
    指定ユーザーが他ユーザーに共有したタスク一覧を取得する
    
    Args:
        user_id (int): 共有したタスクを取得するユーザーのID
        
    Returns:
        list: 共有したタスク情報と共有先ユーザーIDのタプルのリスト（shared_withカラム含む）
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            """
            SELECT tasks.*, task_shares.user_id AS shared_with
            FROM tasks
            JOIN task_shares ON tasks.id = task_shares.task_id
            WHERE tasks.user = ?
            """,
            (user_id,)
        )
        return await cursor.fetchall()