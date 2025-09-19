import aiosqlite
import bcrypt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH
import re

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

def validate_email(email):
    """
    メールアドレスの形式を検証する
    
    Args:
        email (str): 検証するメールアドレス
        
    Returns:
        bool: 有効なメールアドレス形式の場合True、無効な場合False
    """
        
    # 基本的なメールアドレスの正規表現パターン
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or not isinstance(email, str):
        return False
    
    return re.match(pattern, email) is not None

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
    # validate email format
    if not validate_email(email):
        raise ValueError("Invalid email format")
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

async def delete_task(task_id):
    """
    タスクを削除する
    
    Args:
        task_id (int): 削除するタスクのID
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        # タスク共有も削除
        await conn.execute("DELETE FROM task_shares WHERE task_id = ?", (task_id,))
        # タスク削除
        await conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        await conn.commit()

async def update_task(task_id, name=None, description=None, tag=None, deadline=None, priority=None, is_done=None):
    """
    タスク情報を更新する
    
    Args:
        task_id (int): 更新するタスクのID
        name (str, optional): 新しいタスク名
        description (str, optional): 新しい詳細説明
        tag (int, optional): 新しいタグID
        deadline (datetime, optional): 新しい締め切り日時
        priority (int, optional): 新しい優先度
        is_done (bool, optional): 完了状態（True: 完了済み, False: 未完了）
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        # 更新するフィールドを動的に構築
        updates = []
        params = []
        
        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if tag is not None:
            updates.append("tag = ?")
            params.append(tag)
        if deadline is not None:
            updates.append("deadline = ?")
            params.append(deadline)
        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)
        if is_done is not None:
            updates.append("is_done = ?")
            params.append(1 if is_done else 0)
            if is_done:
                updates.append("completed_at = CURRENT_TIMESTAMP")
            else:
                updates.append("completed_at = NULL")
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(task_id)
            query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
            await conn.execute(query, params)
            await conn.commit()

async def search_tasks(user_id, keyword=None, tag_id=None, is_done=None, priority=None):
    """
    タスクを検索する
    
    Args:
        user_id (int): 検索するユーザーのID
        keyword (str, optional): タスク名や詳細に含まれるキーワード
        tag_id (int, optional): 特定のタグID
        is_done (bool, optional): 完了状態（True: 完了済み, False: 未完了）
        priority (int, optional): 特定の優先度
        
    Returns:
        list: 検索条件に一致するタスク情報のタプルのリスト
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        query = "SELECT * FROM tasks WHERE user = ?"
        params = [user_id]
        
        if keyword:
            query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        if tag_id is not None:
            query += " AND tag = ?"
            params.append(tag_id)
        if is_done is not None:
            query += " AND is_done = ?"
            params.append(1 if is_done else 0)
        if priority is not None:
            query += " AND priority = ?"
            params.append(priority)
            
        cursor = await conn.execute(query, params)
        return await cursor.fetchall()

async def get_tasks_sorted(user_id, sort_by="created_at", order="ASC"):
    """
    ソート済みのタスク一覧を取得する
    
    Args:
        user_id (int): タスクを取得するユーザーのID
        sort_by (str): ソートするカラム名（created_at, deadline, priority, name）
        order (str): ソート順（ASC: 昇順, DESC: 降順）
        
    Returns:
        list: ソート済みタスク情報のタプルのリスト
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        # SQLインジェクション対策でカラム名を検証
        allowed_columns = ["created_at", "deadline", "priority", "name", "is_done"]
        if sort_by not in allowed_columns:
            sort_by = "created_at"
        if order.upper() not in ["ASC", "DESC"]:
            order = "ASC"
            
        query = f"SELECT * FROM tasks WHERE user = ? ORDER BY {sort_by} {order}"
        cursor = await conn.execute(query, (user_id,))
        return await cursor.fetchall()

async def mark_task_undone(task_id):
    """
    タスクを未完了状態にする
    
    Args:
        task_id (int): 未完了にするタスクのID
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE tasks SET is_done = 0, completed_at = NULL WHERE id = ?",
            (task_id,)
        )
        await conn.commit()

async def get_tasks_by_deadline(user_id, start_date=None, end_date=None):
    """
    締め切り日範囲でタスクを取得する（リマインダー機能用）
    
    Args:
        user_id (int): タスクを取得するユーザーのID
        start_date (datetime, optional): 開始日時
        end_date (datetime, optional): 終了日時
        
    Returns:
        list: 指定期間内の締め切りがあるタスク情報のタプルのリスト
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        query = "SELECT * FROM tasks WHERE user = ? AND deadline IS NOT NULL"
        params = [user_id]
        
        if start_date:
            query += " AND deadline >= ?"
            params.append(start_date)
        if end_date:
            query += " AND deadline <= ?"
            params.append(end_date)
            
        query += " ORDER BY deadline ASC"
        cursor = await conn.execute(query, params)
        return await cursor.fetchall()

async def get_task_by_id(task_id):
    """
    タスクIDで特定のタスク情報を取得する
    
    Args:
        task_id (int): 取得するタスクのID
        
    Returns:
        tuple or None: タスク情報のタプル、見つからない場合はNone
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return await cursor.fetchone()

async def unshare_task(task_id, user_id=None):
    """
    タスクの共有を解除する
    
    Args:
        task_id (int): 共有解除するタスクのID
        user_id (int, optional): 特定ユーザーのみ共有解除。Noneの場合は全ユーザーの共有を解除
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        if user_id:
            await conn.execute(
                "DELETE FROM task_shares WHERE task_id = ? AND user_id = ?",
                (task_id, user_id)
            )
        else:
            await conn.execute(
                "DELETE FROM task_shares WHERE task_id = ?",
                (task_id,)
            )
        await conn.commit()

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

async def delete_tag(tag_id):
    """
    タグを削除する
    
    Args:
        tag_id (int): 削除するタグのID
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        # タグを使用しているタスクのタグをNULLに設定
        await conn.execute("UPDATE tasks SET tag = NULL WHERE tag = ?", (tag_id,))
        # タグ削除
        await conn.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        await conn.commit()

async def get_tag_by_id(tag_id):
    """
    タグIDで特定のタグ情報を取得する
    
    Args:
        tag_id (int): 取得するタグのID
        
    Returns:
        tuple or None: タグ情報のタプル、見つからない場合はNone
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
        return await cursor.fetchone()
    
async def reminder_create(user_id, task_id, remind_at):
    """
    新しいリマインダーを作成する
    
    Args:
        user_id (int): リマインダーを作成するユーザーのID
        task_id (int): リマインダー対象のタスクID
        remind_at (datetime): リマインド日時
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "INSERT INTO reminders (user, task_id, remind_at) VALUES (?, ?, ?)",
            (user_id, task_id, remind_at)
        )
        await conn.commit()

async def get_upcoming_reminders(current_time):
    """
    指定日時以降のリマインダー一覧を取得する
    
    Args:
        current_time (datetime): 現在日時
        
    Returns:
        list: 指定日時以降のリマインダー情報のタプルのリスト
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(
            "SELECT * FROM reminders WHERE remind_at >= ? ORDER BY remind_at ASC",
            (current_time,)
        )
        return await cursor.fetchall()
    
async def delete_reminder(reminder_id):
    """
    リマインダーを削除する
    
    Args:
        reminder_id (int): 削除するリマインダーのID
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        await conn.commit()

async def get_reminders_by_user(user_id):
    """
    指定ユーザーのリマインダー一覧を取得する
    
    Args:
        user_id (int): リマインダーを取得するユーザーのID
        
    Returns:
        list: リマインダー情報のタプルのリスト
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute("SELECT * FROM reminders WHERE user = ?", (user_id,))
        return await cursor.fetchall()
    
async def update_reminder(reminder_id, remind_at=None):
    """
    リマインダー情報を更新する
    
    Args:
        reminder_id (int): 更新するリマインダーのID
        remind_at (str): 新しいリマインド日時("YYYY-MM-DD HH:MM:SS"形式)
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        updates = []
        params = []
        
        if remind_at is not None:
            updates.append("remind_at = ?")
            params.append(remind_at)
        
        if updates:
            params.append(reminder_id)
            query = f"UPDATE reminders SET {', '.join(updates)} WHERE id = ?"
            await conn.execute(query, params)
            await conn.commit()

async def get_reminders_by_tasks(task_ids):
    """
    複数タスクに紐づくリマインダー一覧を取得する
    
    Args:
        task_ids (list): タスクIDのリスト
        
    Returns:
        list: 指定タスクに紐づくリマインダー情報のタプルのリスト
    """
    if not task_ids:
        return []
    
    placeholders = ','.join('?' for _ in task_ids)
    query = f"SELECT * FROM reminders WHERE task_id IN ({placeholders})"
    
    async with aiosqlite.connect(DB_PATH) as conn:
        cursor = await conn.execute(query, task_ids)
        return await cursor.fetchall()

async def done_reminder(reminder_id):
    """
    リマインダーを完了状態にする
    
    Args:
        reminder_id (int): 完了にするリマインダーのID
        
    Returns:
        None
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute(
            "UPDATE reminders SET is_sent = 1 WHERE id = ?",
            (reminder_id,)
        )
        await conn.commit()