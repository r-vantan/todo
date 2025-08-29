import tkinter as tk
from lib.tasks import TaskManager
from lib.session import get_current_user_id

task_manager: TaskManager = TaskManager()

class TodoPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # UI
        logout_button = tk.Button(self, text="ログアウト")
        logout_button.pack(pady=10)

        # タスク一覧表示エリア
        self.task_listbox = tk.Listbox(self)
        self.task_listbox.pack(pady=10)

        # タスク追加エリア
        self.new_task_entry = tk.Entry(self)
        self.new_task_entry.pack(pady=10)

        add_task_button = tk.Button(self, text="タスク追加")
        add_task_button.pack(pady=10)

        refresh_button = tk.Button(self, text="タスク更新")
        refresh_button.pack(pady=10)

        # タスク共有エリア
        self.shared_task_listbox = tk.Listbox(self)
        self.shared_task_listbox.pack(pady=10)

        ##---------##

    def get_tasks(self):
        user_id = get_current_user_id()
        tasks = task_manager.get_by_user(user_id)
        return tasks

    def get_shared_tasks(self):
        user_id = get_current_user_id()
        shared_tasks = task_manager.get_shared_tasks(user_id)
        return shared_tasks