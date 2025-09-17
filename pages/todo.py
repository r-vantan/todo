import customtkinter as tk
from lib.tasks import TaskManager
from lib.session import get_current_user_id
from lib.session import logout as db_logout
import asyncio
from PIL import Image

task_manager: TaskManager = TaskManager()

class TodoPage(tk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # UI
        logout_button = tk.CTkButton(self, text="ログアウト", command=self.logout)
        logout_button.pack(pady=10)

        # タスク一覧表示エリア（タスクごとにFrameで表示）
        self.task_list_frame = tk.CTkFrame(self)
        self.task_list_frame.pack(pady=10, fill="x")

        # タスク追加エリア
        self.new_task_entry = tk.CTkEntry(self)
        self.new_task_entry.pack(pady=10)

        add_task_button = tk.CTkButton(self, text="タスク追加", command=self.add_task)
        add_task_button.pack(pady=10)

        # 完了・エラー表示用ラベル（常に空間を空けておく）
        self.status_label = tk.CTkLabel(self, text="", fg_color="transparent")
        self.status_label.pack(pady=10)

        refresh_button = tk.CTkButton(self, text="タスク更新", command=self.refresh_tasks)
        refresh_button.pack(pady=10)

        # タスク共有エリア（共有タスクもFrameで表示）
        self.shared_task_list_frame = tk.CTkFrame(self)
        self.shared_task_list_frame.pack(pady=10, fill="x")

        self.refresh_tasks()

    def add_task(self):
        name = self.new_task_entry.get()
        if name:
            user_id = get_current_user_id()
            try:
                # 引数を明示的に渡す
                asyncio.run(task_manager.create(user_id, name=name, description=None, tag=None, deadline=None, priority=0))
                self.new_task_entry.delete(0, tk.END)
                self.refresh_tasks()
                self.status_label.configure(text="タスクを追加しました", fg_color="green")
            except Exception as e:
                self.status_label.configure(text=f"エラー: {e}", fg_color="red")
        else:
            self.status_label.configure(text="タスク名を入力してください", fg_color="red")

    def get_tasks(self):
        user_id = get_current_user_id()
        # TaskManager.get_by_userはリストを返す
        tasks = asyncio.run(task_manager.get_by_user(user_id))
        return tasks

    def refresh_tasks(self):
        # タスク一覧Frameの中身をクリア
        for widget in self.task_list_frame.winfo_children():
            widget.destroy()
        tasks = self.get_tasks()
        for task in tasks:
            task_id, name = task[0], task[4]  # nameのインデックスを修正
            row_frame = tk.CTkFrame(self.task_list_frame)
            row_frame.pack(fill="x", pady=2)
            label = tk.CTkLabel(row_frame, text=f"{name}", width=200, anchor="w")
            label.pack(side="left", padx=5)
            trash_img = tk.CTkImage(
                light_image=Image.open("static/trash.png"), size=(20, 20)
            )
            edit_img = tk.CTkImage(
                light_image=Image.open("static/edit.png"), size=(20, 20)
            )
            del_btn = tk.CTkButton(row_frame, image=trash_img, text="", width=30,command=lambda tid=task_id: self.delete_task(tid))
            del_btn.pack(side="left", padx=5)
            edit_btn = tk.CTkButton(row_frame, image=edit_img,text="", width=30, command=lambda tid=task_id, nm=name: self.open_edit_popup(tid, nm))
            edit_btn.pack(side="left", padx=5)

        # 共有タスクもFrameで表示
        for widget in self.shared_task_list_frame.winfo_children():
            widget.destroy()
        shared_tasks = self.get_shared_tasks()
        for task in shared_tasks:
            task_id, name = task[0], task[1]  # nameのインデックスを修正
            row_frame = tk.CTkFrame(self.shared_task_list_frame)
            row_frame.pack(fill="x", pady=2)
            trash_img = tk.CTkImage(
                light_image=Image.open("static/trash.png"), size=(20, 20)
            )
            edit_img = tk.CTkImage(
                light_image=Image.open("static/edit.png"), size=(20, 20)
            )
            label = tk.CTkLabel(row_frame, text=f"{name} (共有)", width=200, anchor="w")
            label.pack(side="left", padx=5)
            del_btn = tk.CTkButton(row_frame, image=trash_img, text="", width=30, command=lambda tid=task_id: self.delete_task(tid))
            del_btn.pack(side="left", padx=5)
            edit_btn = tk.CTkButton(row_frame, image=edit_img, text="", width=30, command=lambda tid=task_id, nm=name: self.open_edit_popup(tid, nm))
            edit_btn.pack(side="left", padx=5)

    def delete_task(self, task_id):
        try:
            asyncio.run(task_manager.delete(task_id))
            self.refresh_tasks()
            self.status_label.configure(text="タスクを削除しました", fg_color="green")
        except Exception as e:
            self.status_label.configure(text=f"削除エラー: {e}", fg_color="red")

    def open_edit_popup(self, task_id, name):
        popup = tk.CTkToplevel(self)
        popup.title("タスク編集")
        popup.geometry("300x150")
        label = tk.CTkLabel(popup, text="新しい名前:")
        label.pack(pady=10)
        entry = tk.CTkEntry(popup)
        entry.insert(0, name)
        entry.pack(pady=5)
        desc_label = tk.CTkLabel(popup, text="新しい説明:")
        desc_label.pack(pady=10)
        entry_desc = tk.CTkEntry(popup)
        entry_desc.pack(pady=5)
        def save():
            new_name = entry.get()
            new_desc = entry_desc.get()
            try:
                asyncio.run(task_manager.update(task_id, name=new_name, description=new_desc))
                self.refresh_tasks()
                self.status_label.configure(text="タスクを更新しました", fg_color="green")
                popup.destroy()
            except Exception as e:
                self.status_label.configure(text=f"更新エラー: {e}", fg_color="red")
        save_btn = tk.CTkButton(popup, text="保存", command=save)
        save_btn.pack(pady=10)

    def get_shared_tasks(self):
        user_id = get_current_user_id()
        # TaskManager.get_shared_with_meはリストを返す
        shared_tasks = asyncio.run(task_manager.get_shared_with_me(user_id))
        return shared_tasks

    def logout(self):
        db_logout()
        self.controller.show_frame("login")
