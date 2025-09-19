from utils.db import (
    reminder_create,
    get_upcoming_reminders,
    delete_reminder,
    get_reminders_by_user,
    update_reminder,
    get_reminders_by_task,
    done_reminder
)
from datetime import datetime, timedelta
import asyncio
from plyer import notification
from lib.tasks import TaskManager
import threading
import json
import aiofiles

taskmanager: TaskManager = TaskManager()

class ReminderManager:
    @staticmethod
    async def create_reminder(task_id: int, remind_at: str):
        return await reminder_create(task_id, remind_at)

    @staticmethod
    async def fetch_upcoming_reminders():
        return await get_upcoming_reminders()
    
    @staticmethod
    async def fetch_reminder(reminder_id: int):
        reminders = await get_reminders_by_task(reminder_id)
        if reminders:
            return reminders[0]
        return None

    @staticmethod
    async def remove_reminder(reminder_id: int):
        return await delete_reminder(reminder_id)

    @staticmethod
    async def fetch_reminders_by_user(user_id: int):
        return await get_reminders_by_user(user_id)

    @staticmethod
    async def modify_reminder(reminder_id: int, new_remind_at: str):
        return await update_reminder(reminder_id, new_remind_at)

    @staticmethod
    async def fetch_reminders_by_task(task_id: int):
        return await get_reminders_by_task(task_id)
    
    @staticmethod
    async def done_reminder(reminder_id: int):
        return await done_reminder(reminder_id)
    
    @staticmethod
    async def should_send_reminder(user_id: int):
        """
        リマインドするべきタスクをリストで返す

        Args:
            user_id (int): ユーザーID

        Returns:
            list: [[task_id, reminder_id], ...]

        """
        reminders = await get_reminders_by_user(user_id)
        now = datetime.now()
        tasks_to_remind = []
        for reminder in reminders:
            # reminder: (id, task_id, remind_at, is_sent)
            remind_at = datetime.fromisoformat(reminder[2])
            if now >= remind_at:
                tasks_to_remind.append([reminder[1], reminder[0]])
        return tasks_to_remind

    @staticmethod
    async def update_reminder_for_task(task_id: int, old_deadline: datetime, new_deadline: datetime):
        reminders = await get_reminders_by_task(task_id)
        for reminder in reminders:
            remind_at = datetime.fromisoformat(reminder[2])
            if reminder[3] == 1:  # is_sent
                continue
            if old_deadline > remind_at:
                time_diff = old_deadline - remind_at
                new_remind_at = new_deadline - time_diff
                await update_reminder(reminder[0], new_remind_at.isoformat())

async def send_notification(task_id: int, reminder_id: int):
    task = await taskmanager.get_by_id(task_id)
    task_name = task[4]
    reminder = await ReminderManager.fetch_reminder(reminder_id)
    reminder_time = reminder[2]
    time_diff: timedelta = datetime.fromisoformat(reminder_time) - datetime.fromisoformat(task[7])
    notification.notify(
        title="リマインダー",
        message=f"{task_name}の締切まであと{int(time_diff.total_seconds() // 60)}分です。",
        timeout=10
    )

def run_send_notification(task_id: int, reminder_id: int):
    asyncio.run(send_notification(task_id, reminder_id))

async def reminder_loop():
    while True:
        async with aiofiles.open('session.json', 'r') as f:
            session_data = json.loads(await f.read())
        user_id = session_data.get("user_id")
        if not user_id:
            await asyncio.sleep(60)
            continue
        should_send = await ReminderManager.should_send_reminder(user_id)
        for reminder in should_send:
            threading.Thread(target=run_send_notification, args=(reminder[0], reminder[1])).start()
            print(f"Reminder for user {reminder[0]} about task {reminder[1]}")
            await ReminderManager.done_reminder(reminder[1])
        await asyncio.sleep(60)  # 1分ごとにチェック