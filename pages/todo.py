import customtkinter as tk
from lib.tasks import TaskManager
from lib.tags import TagManager
from lib.session import get_current_user_id
from lib.session import logout as db_logout
import asyncio
from aiosqlite import IntegrityError
from PIL import Image

task_manager: TaskManager = TaskManager()
tag_manager: TagManager = TagManager()

priority = ["無", "低", "中", "高", "最高"]

class PlaceholderCTkEntry(tk.CTkEntry):
    def __init__(self, master, placeholder, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "grey"
        self.default_color = "black"
        self._is_password = "show" in kwargs
        self._is_placeholder_active = True  # プレースホルダー状態を明示的に管理

        if self._is_password:
            self.configure(show="")

        self.insert(0, self.placeholder)
        self.configure(text_color=self.placeholder_color)

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event):
        if self._is_placeholder_active:
            self.delete(0, tk.END)
            self.configure(text_color="white")
            self._is_placeholder_active = False
            if self._is_password:
                self.configure(show="*")

    def _on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(text_color=self.placeholder_color)
            self._is_placeholder_active = True
            if self._is_password:
                self.configure(show="", text_color=self.placeholder_color)

    def clear_to_placeholder(self):
        """値をクリアしてプレースホルダーに戻す"""
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
        self.configure(text_color=self.placeholder_color)
        self._is_placeholder_active = True
        if self._is_password:
            self.configure(show="")
        # フォーカスを外す
        if self.focus_get() == self:
            self.master.focus_set()
    
    def get_real_value(self):
        """プレースホルダーではない実際の値を取得"""
        if self._is_placeholder_active:
            return ""
        return self.get()

class TodoPage(tk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # UI
        logout_button = tk.CTkButton(self, text="ログアウト", command=self.logout)
        logout_button.pack(pady=10)

        # タスク検索
        self.search_entry = PlaceholderCTkEntry(self, placeholder="入力して検索...")
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_tasks())

        # タスク並び替え
        self.sort_var = tk.StringVar(value="作成日")
        sort_options = ["作成日", "期限日", "優先度", "名前"]
        sort_menu = tk.CTkOptionMenu(self, variable=self.sort_var, values=sort_options, command=lambda v: self.refresh_tasks())
        sort_menu.pack(pady=5)

        # 昇順・降順切替
        self.order_var = tk.StringVar(value="昇順")
        order_options = ["昇順", "降順"]
        order_menu = tk.CTkOptionMenu(self, variable=self.order_var, values=order_options, command=lambda v: self.refresh_tasks())
        order_menu.pack(pady=5)

        # タグフィルタ
        self.tag_filter_var = tk.StringVar(value="すべて")
        self.tag_id_dict = {}  # タグ名→IDの辞書
        self.tag_list = ["すべて"]  # 初期値、後で動的に更新可
        self.tag_filter_menu = tk.CTkOptionMenu(self, variable=self.tag_filter_var, values=self.tag_list, command=lambda v: self.refresh_tasks())
        self.tag_filter_menu.pack(pady=5)

        # タスク一覧表示エリア（タスクごとにFrameで表示）
        self.task_list_frame = tk.CTkFrame(self)
        self.task_list_frame.pack(pady=10, fill="x")

        # タスク追加エリア
        self.new_task_entry = tk.CTkEntry(self)
        self.new_task_entry.pack(pady=10)
        self.new_task_entry.bind("<Return>", lambda e: self.add_task())

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
                self.status_label.configure(text="タスクを追加しました", text_color="green")
            except Exception as e:
                self.status_label.configure(text=f"エラー: {e}", text_color="red")
        else:
            self.status_label.configure(text="タスク名を入力してください", text_color="red")

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
        # タグ一覧を更新
        tags = asyncio.run(tag_manager.get_by_user(get_current_user_id()))
        tag_filter_values = ["すべて"] + [str(t[2]) for t in tags]  # タグ名のリスト
        self.tag_id_dict = {str(t[2]): t[0] for t in tags}  # タグ名→IDの辞書
        self.tag_filter_menu.configure(values=tag_filter_values)

        # 検索フィルタ適用
        search_text = self.search_entry.get_real_value()
        if search_text:
            tasks = asyncio.run(task_manager.search(get_current_user_id(), keyword=search_text))

        # タグフィルタ適用
        selected_tag = self.tag_filter_var.get()
        if selected_tag != "すべて":
            selected_tag_id = self.tag_id_dict.get(selected_tag)
            tasks = [t for t in tasks if t[6] == selected_tag_id]

        # 並び替え適用
        sort_key = self.sort_var.get()
        reverse = self.order_var.get() == "降順"
        if sort_key == "作成日":
            tasks.sort(key=lambda x: x[9], reverse=reverse)  # 作成日でソート
        elif sort_key == "期限日":
            tasks.sort(key=lambda x: (x[7] is None, x[7]), reverse=reverse)  # 締切でソート、Noneは最後
        elif sort_key == "優先度":
            tasks.sort(key=lambda x: x[8], reverse=reverse)  # 優先度でソート
        elif sort_key == "名前":
            tasks.sort(key=lambda x: x[4].lower(), reverse=reverse)  # 名前でソート（大文字小文字区別なし）

        for task in tasks:
            # DB設計に合わせてインデックス修正
            task_id = task[0]
            name = task[4]
            is_done = bool(task[3])  # 0/1→False/True
            tag_id = task[6]
            # タグ名取得（tag_idがNoneならDBアクセスしない）
            if tag_id:
                tag_info = asyncio.run(tag_manager.get_by_id(tag_id))
                tag_name = tag_info[2] if tag_info else ""
            else:
                tag_name = ""
            row_frame = tk.CTkFrame(self.task_list_frame)
            row_frame.pack(fill="x", pady=2)
            # 完了チェックボックス
            is_done_var = tk.BooleanVar(value=is_done)
            done_check = tk.CTkCheckBox(row_frame, text="", variable=is_done_var,
                command=lambda tid=task_id, v=is_done_var: self.toggle_done(tid, v.get()))
            done_check.pack(side="left", padx=5)
            # 名前
            label = tk.CTkLabel(row_frame, text=f"{name}", width=200, anchor="w")
            label.pack(side="left", padx=5)
            label.bind("<Double-Button-1>", lambda e, tid=task_id: self.show_detail_popup(tid))
            # タグ
            tag_label = tk.CTkLabel(row_frame, text=tag_name if tag_name else "", width=60)
            tag_label.pack(side="left", padx=5)
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
            task_id, name = task[0], task[1]
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
            label.bind("<Double-Button-1>", lambda e, tid=task_id: self.show_detail_popup(tid))
            del_btn = tk.CTkButton(row_frame, image=trash_img, text="", width=30, command=lambda tid=task_id: self.delete_task(tid))
            del_btn.pack(side="left", padx=5)
            edit_btn = tk.CTkButton(row_frame, image=edit_img, text="", width=30, command=lambda tid=task_id, nm=name: self.open_edit_popup(tid, nm))
            edit_btn.pack(side="left", padx=5)

    def toggle_done(self, task_id, is_done):
        try:
            asyncio.run(task_manager.update(task_id, is_done=is_done))
            self.refresh_tasks()
        except Exception as e:
            self.status_label.configure(text=f"完了状態更新エラー: {e}", text_color="red")

    def show_detail_popup(self, task_id):
        # タスク詳細取得
        task = asyncio.run(task_manager.get_by_id(task_id))
        # タスク構造例: (id, name, description, tag, deadline, priority, ...)
        popup = tk.CTkToplevel(self)
        popup.title("タスク詳細")
        popup.geometry("350x250")
        tag_name = asyncio.run(tag_manager.get_by_id(task[6]))[2] if task[6] else "なし"
        detail_text = f"ID: {task[0]}\n名前: {task[4]}\n説明: {task[5]}\nタグ: {tag_name}\n締切: {task[7]}\n優先度: {priority[task[8]]}"
        label = tk.CTkLabel(popup, text=detail_text, anchor="w", justify="left")
        label.pack(padx=20, pady=20)
        close_btn = tk.CTkButton(popup, text="閉じる", command=popup.destroy)
        close_btn.pack(pady=10)

    def delete_task(self, task_id):
        try:
            asyncio.run(task_manager.delete(task_id))
            self.refresh_tasks()
            self.status_label.configure(text="タスクを削除しました", text_color="green")
        except Exception as e:
            self.status_label.configure(text=f"削除エラー: {e}", text_color="red")

    def open_edit_popup(self, task_id, name):
        popup = tk.CTkToplevel(self)
        popup.title("タスク編集")
        popup.geometry("350x550")

        # 名前
        name_label = tk.CTkLabel(popup, text="名前:")
        name_label.pack(pady=(20, 0))
        name_entry = tk.CTkEntry(popup)
        name_entry.insert(0, name)
        name_entry.pack(pady=5)

        # 説明
        desc_label = tk.CTkLabel(popup, text="説明:")
        desc_label.pack(pady=(15, 0))
        desc_entry = tk.CTkEntry(popup)
        desc_entry.pack(pady=5)

        # タグ（DBから取得してリスト化）
        tag_label = tk.CTkLabel(popup, text="タグ:")
        tag_label.pack(pady=(15, 0))
        tag_frame = tk.CTkFrame(popup)
        tag_frame.pack(pady=5)
        tag_options = self.get_tag_list()  # 例: [(id, user_id, name), ...]
        tag_names = [str(t[2]) for t in tag_options]
        if "なし" not in tag_names:
            tag_names = ["なし"] + tag_names
        # 現在のタグIDを取得
        task = asyncio.run(task_manager.get_by_id(task_id))
        current_tag_id = task[6] if len(task) > 6 else None
        if current_tag_id:
            tag_info = asyncio.run(tag_manager.get_by_id(current_tag_id))
            current_tag_name = str(tag_info[2]) if tag_info else "なし"
        else:
            current_tag_name = "なし"
        # 初期値を現在のタグ名に
        tag_var = tk.StringVar(value=current_tag_name if current_tag_name in tag_names else tag_names[0])
        tag_menu = tk.CTkOptionMenu(tag_frame, variable=tag_var, values=tag_names)
        tag_menu.pack(side="left")
        add_tag_btn = tk.CTkButton(tag_frame, text="＋", width=30, command=lambda: self.open_add_tag_popup(tag_menu, tag_var))
        add_tag_btn.pack(side="left", padx=5)

        try:
            from tkcalendar import DateEntry
            deadline_label = tk.CTkLabel(popup, text="締切:")
            deadline_label.pack(pady=(15, 0))
            # ダークテーマ用色設定
            deadline_entry = DateEntry(
                popup,
                date_pattern='yyyy年mm月dd日',
                locale='ja_JP',
                firstweekday='sunday',
                background="#222222",
                foreground="#ffffff",
                bordercolor="#444444",
                headersbackground="#333333",
                headersforeground="#ffffff",
                selectbackground="#00bfff",
                selectforeground="#ffffff",
                normalforeground="#ffffff",
                weekendforeground="#ffffff",
                othermonthforeground="#ffffff",
                disabledforeground="#ffffff"
            )
            deadline_entry.pack(pady=5)
        except ImportError:
            deadline_label = tk.CTkLabel(popup, text="締切 (YYYY-MM-DD):")
            deadline_label.pack(pady=(15, 0))
            deadline_entry = tk.CTkEntry(popup)
            deadline_entry.pack(pady=5)

        # 優先度
        priority_label = tk.CTkLabel(popup, text="優先度:")
        priority_label.pack(pady=(15, 0))
        task = asyncio.run(task_manager.get_by_id(task_id))
        priority_var = tk.StringVar(value=priority[task[8]])
        priority_menu = tk.CTkOptionMenu(popup, variable=priority_var, values=priority)
        priority_menu.pack(pady=5)

        # 完了状態
        is_done_var = tk.BooleanVar(value=False)
        is_done_check = tk.CTkCheckBox(popup, text="完了", variable=is_done_var)
        is_done_check.pack(pady=(15, 0))

        # 保存・キャンセルボタン
        btn_frame = tk.CTkFrame(popup)
        btn_frame.pack(pady=20)
        def save():
            new_name = name_entry.get()
            new_desc = desc_entry.get()
            selected_tag_name = tag_var.get()
            # タグID取得（"なし"ならNone、そうでなければIDを取得）
            if selected_tag_name == "なし":
                new_tag_id = None
            else:
                tag_options = self.get_tag_list()
                tag_dict = {str(t[2]): t[0] for t in tag_options}
                new_tag_id = tag_dict.get(selected_tag_name, None)
            new_deadline = deadline_entry.get()
            new_priority = priority.index(priority_var.get())
            new_is_done = is_done_var.get()
            try:
                asyncio.run(task_manager.update(
                    task_id,
                    name=new_name,
                    description=new_desc,
                    tag=new_tag_id,
                    deadline=new_deadline,
                    priority=new_priority,
                    is_done=new_is_done
                ))
                self.refresh_tasks()
                self.status_label.configure(text="タスクを更新しました", text_color="green")
                popup.destroy()
            except Exception as e:
                self.status_label.configure(text=f"更新エラー: {e}", text_color="red")
        save_btn = tk.CTkButton(btn_frame, text="保存", command=save)
        save_btn.pack(side="left", padx=10)
        cancel_btn = tk.CTkButton(btn_frame, text="キャンセル", command=popup.destroy)
        cancel_btn.pack(side="left", padx=10)

    def open_add_tag_popup(self, tag_menu, tag_var):
        popup = tk.CTkToplevel(self)
        popup.title("タグ新規作成")
        popup.geometry("300x300")
        name_label = tk.CTkLabel(popup, text="タグ名:")
        name_label.pack(pady=(20, 0))
        name_entry = tk.CTkEntry(popup)
        name_entry.pack(pady=5)
        error_label = tk.CTkLabel(popup, text="", text_color="red")
        error_label.pack()
        def save():
            name = name_entry.get()
            user_id = get_current_user_id()
            try:
                asyncio.run(tag_manager.create(user_id, name))
                # タグ一覧を再取得してOptionMenuに反映
                tag_options = self.get_tag_list()
                tag_names = [str(t[2]) for t in tag_options]
                tag_menu.configure(values=tag_names)
                if name in tag_names:
                    tag_var.set(name)
                popup.destroy()
            except IntegrityError:
                error_label.configure(text="タグ名が重複しています", text_color="red")
            except Exception as e:
                error_label.configure(text=f"エラー: {e}", text_color="red")
        save_btn = tk.CTkButton(popup, text="保存", command=save)
        save_btn.pack(pady=10)
        cancel_btn = tk.CTkButton(popup, text="キャンセル", command=popup.destroy)
        cancel_btn.pack(pady=5)

    def get_tag_list(self):
        # DBからタグ一覧取得
        return asyncio.run(tag_manager.get_by_user(get_current_user_id()))

    def get_shared_tasks(self):
        user_id = get_current_user_id()
        # TaskManager.get_shared_with_meはリストを返す
        shared_tasks = asyncio.run(task_manager.get_shared_with_me(user_id))
        return shared_tasks

    def logout(self):
        db_logout()
        self.controller.show_frame("login")
