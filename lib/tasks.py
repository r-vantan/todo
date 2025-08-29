from utils.db import (
    create_task,
    get_tasks_by_user,
    get_task_by_id,
    update_task,
    delete_task,
    mark_task_done,
    mark_task_undone,
    search_tasks,
    get_tasks_sorted,
    get_tasks_by_deadline,
    share_task,
    get_shared_tasks,
    get_shared_tasks_by_user,
    unshare_task
)

class TaskManager:
    """タスク管理のためのライブラリクラス"""
    
    @staticmethod
    async def create(user_id, name, description=None, tag=None, deadline=None, priority=0):
        """新しいタスクを作成する"""
        await create_task(user_id, name, description, tag, deadline, priority)
    
    @staticmethod
    async def get_by_user(user_id):
        """ユーザーのタスク一覧を取得する"""
        return await get_tasks_by_user(user_id)
    
    @staticmethod
    async def get_by_id(task_id):
        """IDでタスクを取得する"""
        return await get_task_by_id(task_id)
    
    @staticmethod
    async def update(task_id, **kwargs):
        """タスク情報を更新する"""
        await update_task(task_id, **kwargs)
    
    @staticmethod
    async def delete(task_id):
        """タスクを削除する"""
        await delete_task(task_id)
    
    @staticmethod
    async def mark_complete(task_id):
        """タスクを完了にする"""
        await mark_task_done(task_id)
    
    @staticmethod
    async def mark_incomplete(task_id):
        """タスクを未完了にする"""
        await mark_task_undone(task_id)
    
    @staticmethod
    async def search(user_id, **filters):
        """タスクを検索する"""
        return await search_tasks(user_id, **filters)
    
    @staticmethod
    async def get_sorted(user_id, sort_by="created_at", order="ASC"):
        """ソート済みタスク一覧を取得する"""
        return await get_tasks_sorted(user_id, sort_by, order)
    
    @staticmethod
    async def get_by_deadline_range(user_id, start_date=None, end_date=None):
        """締切日範囲でタスクを取得する"""
        return await get_tasks_by_deadline(user_id, start_date, end_date)
    
    @staticmethod
    async def share_with_users(task_id, user_ids):
        """タスクを他ユーザーと共有する"""
        await share_task(task_id, user_ids)
    
    @staticmethod
    async def get_shared_with_me(user_id):
        """自分に共有されたタスク一覧を取得する"""
        return await get_shared_tasks(user_id)
    
    @staticmethod
    async def get_shared_by_me(user_id):
        """自分が共有したタスク一覧を取得する"""
        return await get_shared_tasks_by_user(user_id)
    
    @staticmethod
    async def unshare(task_id, user_id=None):
        """タスクの共有を解除する"""
        await unshare_task(task_id, user_id)

# 便利な関数も提供
async def get_user_tasks(user_id, include_shared=False):
    """ユーザーのタスクを取得（共有タスクも含めるかオプション）"""
    own_tasks = await TaskManager.get_by_user(user_id)
    if include_shared:
        shared_tasks = await TaskManager.get_shared_with_me(user_id)
        return own_tasks + shared_tasks
    return own_tasks

async def get_pending_tasks(user_id):
    """未完了タスクのみを取得"""
    return await TaskManager.search(user_id, is_done=False)

async def get_completed_tasks(user_id):
    """完了タスクのみを取得"""
    return await TaskManager.search(user_id, is_done=True)

async def get_high_priority_tasks(user_id, priority_threshold=2):
    """高優先度タスクを取得"""
    tasks = await TaskManager.get_by_user(user_id)
    return [task for task in tasks if task[6] >= priority_threshold]  # priority is at index 6