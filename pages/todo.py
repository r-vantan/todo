import customtkinter as tk
from lib.tasks import TaskManager
from lib.tags import TagManager
from lib.reminder import ReminderManager
from lib.users import UserManager
from lib.session import get_current_user_id
from lib.session import logout as db_logout
import asyncio
from aiosqlite import IntegrityError
from PIL import Image

task_manager: TaskManager = TaskManager()
tag_manager: TagManager = TagManager()
reminder_manager: ReminderManager = ReminderManager()
user_manager: UserManager = UserManager()

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

        trash_img = tk.CTkImage(
            light_image=Image.open("static/trash.png"), size=(20, 20)
        )
        edit_img = tk.CTkImage(
            light_image=Image.open("static/edit.png"), size=(20, 20)
        )
        reminder_img = tk.CTkImage(
            light_image=Image.open("static/bell.png"), size=(20, 20)
        )
        share_img = tk.CTkImage(
            light_image=Image.open("static/share.png"), size=(20, 20)
        )

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
            del_btn = tk.CTkButton(row_frame, image=trash_img, text="", width=30,command=lambda tid=task_id: self.delete_task(tid))
            del_btn.pack(side="left", padx=5)
            edit_btn = tk.CTkButton(row_frame, image=edit_img,text="", width=30, command=lambda tid=task_id, nm=name: self.open_edit_popup(tid, nm))
            edit_btn.pack(side="left", padx=5)
            reminder_btn = tk.CTkButton(row_frame, image=reminder_img, text="", width=30, command=lambda tid=task_id: self.open_reminder_popup(tid))
            reminder_btn.pack(side="left", padx=5)
            share_btn = tk.CTkButton(row_frame, image=share_img, text="", width=30, command=lambda tid=task_id: self.open_share_popup(tid))
            share_btn.pack(side="left", padx=5)

        # 共有タスクもFrameで表示
        for widget in self.shared_task_list_frame.winfo_children():
            widget.destroy()
        shared_tasks = self.get_shared_tasks()
        for task in shared_tasks:
            # タスク構造: (id, user, created_at, is_done, name, description, tag, deadline, priority)
            task_id, name = task[0], task[4]  # nameは5番目のフィールド（インデックス4）
            row_frame = tk.CTkFrame(self.shared_task_list_frame)
            row_frame.pack(fill="x", pady=2)
            label = tk.CTkLabel(row_frame, text=f"{name} (共有)", width=200, anchor="w")
            label.pack(side="left", padx=5)
            label.bind("<Double-Button-1>", lambda e, tid=task_id: self.show_detail_popup(tid))
            del_btn = tk.CTkButton(row_frame, image=trash_img, text="", width=30, command=lambda tid=task_id: self.delete_task(tid))
            del_btn.pack(side="left", padx=5)
            edit_btn = tk.CTkButton(row_frame, image=edit_img, text="", width=30, command=lambda tid=task_id, nm=name: self.open_edit_popup(tid, nm))
            edit_btn.pack(side="left", padx=5)
            reminder_btn = tk.CTkButton(row_frame, image=reminder_img, text="", width=30, command=lambda tid=task_id: self.open_reminder_popup(tid))
            reminder_btn.pack(side="left", padx=5)

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
        popup.geometry("350x625")

        # タスク情報を一度だけ取得
        task = asyncio.run(task_manager.get_by_id(task_id))

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

        deadline_value = task[7] if len(task) > 7 else None
        # 日付＋時刻分割
        import re
        date_part, time_part = None, ""
        if deadline_value:
            m = re.match(r"(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2}))?", str(deadline_value))
            if m:
                date_part = m.group(1)
                time_part = m.group(2) if m.group(2) else ""
        try:
            from tkcalendar import DateEntry
            deadline_label = tk.CTkLabel(popup, text="締切日:")
            deadline_label.pack(pady=(15, 0))
            deadline_entry = DateEntry(
                popup,
                date_pattern='yyyy-mm-dd',
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
            if date_part:
                try:
                    deadline_entry.set_date(date_part)
                except Exception:
                    pass
        except ImportError:
            deadline_label = tk.CTkLabel(popup, text="締切日 (YYYY-MM-DD):")
            deadline_label.pack(pady=(15, 0))
            deadline_entry = tk.CTkEntry(popup)
            deadline_entry.pack(pady=5)
            if date_part:
                deadline_entry.insert(0, date_part)

        # 締切なしオプション
        deadline_none_var = tk.BooleanVar(value=not deadline_value)
        deadline_none_check = tk.CTkCheckBox(popup, text="締切なし", variable=deadline_none_var)
        deadline_none_check.pack(pady=5)

        # 時刻入力欄
        time_label = tk.CTkLabel(popup, text="締切時刻 (HH:MM):")
        time_label.pack(pady=(5, 0))
        time_entry = tk.CTkEntry(popup)
        time_entry.pack(pady=5)
        # 時刻は常に00:00を初期値、既存値があればそれを使用
        time_entry.insert(0, time_part if time_part else "00:00")

        # 優先度
        priority_label = tk.CTkLabel(popup, text="優先度:")
        priority_label.pack(pady=(15, 0))
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
            new_date = deadline_entry.get()
            new_time = time_entry.get().strip()
            # 締切なしがチェックされている場合はNone
            if deadline_none_var.get():
                new_deadline = None
            elif new_date and new_time:
                new_deadline = f"{new_date} {new_time}"
            elif new_date:
                new_deadline = new_date
            else:
                new_deadline = None
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

    def open_reminder_popup(self, task_id):
        popup = tk.CTkToplevel(self)
        popup.title("リマインダー管理")
        popup.geometry("400x400")

        # 新規リマインダー追加エリア
        entry_frame = tk.CTkFrame(popup)
        entry_frame.pack(pady=10)
        reminder_entry = tk.CTkEntry(entry_frame, placeholder_text="リマインダー内容")
        reminder_entry.pack(side="left", padx=5)
        def format_content(content):
            """
            形式は(YYYY-MM-DD HH:MM)
            
            contentは1hや30mのような形式を想定する。ただし、1h30mや2h15m10sのように複数組み合わせても良い。
            許容されるのはw,d,h,mのみ
            contentから時間を解析して、現在時刻からの相対時間を計算し、フォーマットする
            """
            import re
            from datetime import datetime, timedelta
            pattern = r'(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?'
            match = re.fullmatch(pattern, content.strip())
            if not match:
                return False
            weeks = int(match.group(1) or 0)
            days = int(match.group(2) or 0)
            hours = int(match.group(3) or 0)
            minutes = int(match.group(4) or 0)
            if weeks == days == hours == minutes == 0:
                return None
            delta = timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes)
            task = asyncio.run(task_manager.get_by_id(task_id))
            deadline_str = task[7]  # 締切日時
            if deadline_str:
                deadline_str = datetime.fromisoformat(str(deadline_str))
            reminder_time = deadline_str - delta
            return reminder_time.strftime("%Y-%m-%d %H:%M")

        def add_reminder():
            content = reminder_entry.get()
            formatted_content = format_content(content)
            if formatted_content is False:
                error_label.configure(text="形式エラー(2d, 1h, 30mのような形式のみ許可されています)", text_color="red")
                return
            if formatted_content:
                asyncio.run(reminder_manager.create_reminder(task_id, formatted_content))
                reminder_entry.delete(0, tk.END)
                refresh_reminder_list()
        add_btn = tk.CTkButton(entry_frame, text="+", width=30, command=add_reminder)
        add_btn.pack(side="left", padx=5)

        # リマインダー一覧表示エリア
        list_frame = tk.CTkFrame(popup)
        list_frame.pack(fill="both", expand=True, pady=10)
        error_label = tk.CTkLabel(popup, text="", text_color="red")
        error_label.pack()

        def refresh_reminder_list():
            for widget in list_frame.winfo_children():
                widget.destroy()
            # DBからリマインダー一覧取得（タプル型返却）
            reminders = asyncio.run(reminder_manager.fetch_reminders_by_task(task_id))
            for reminder in reminders:
                row = tk.CTkFrame(list_frame)
                row.pack(fill="x", pady=2)
                # remind_at（内容）はインデックス2、idはインデックス0
                label = tk.CTkLabel(row, text=reminder[2], anchor="w")
                label.pack(side="left", padx=5)
                del_btn = tk.CTkButton(row, text="削除", width=40, command=lambda rid=reminder[0]: delete_reminder(rid))
                del_btn.pack(side="right", padx=5)

        def delete_reminder(reminder_id):
            # DBからリマインダー削除
            asyncio.run(reminder_manager.remove_reminder(reminder_id))
            refresh_reminder_list()

        refresh_reminder_list()

    def open_share_popup(self, task_id):
        # ユーザーのメールアドレスを入力して共有
        popup = tk.CTkToplevel(self)
        popup.title("タスク共有")
        popup.geometry("400x400")

        # 新規シェア追加エリア
        entry_frame = tk.CTkFrame(popup)
        entry_frame.pack(pady=10)
        email_entry = tk.CTkEntry(entry_frame, placeholder_text="メールアドレス")
        email_entry.pack(side="left", padx=5)

        def add_share():
            email = email_entry.get()
            if not email:
                error_label.configure(text="メールアドレスを入力してください", text_color="red")
                return
            
            try:
                user = asyncio.run(user_manager.get_by_email(email))
                if not user:
                    error_label.configure(text="ユーザーが見つかりません", text_color="red")
                    return
                    
                # 自分自身との共有をチェック
                current_user_id = get_current_user_id()
                if user[0] == current_user_id:
                    error_label.configure(text="自分自身とは共有できません", text_color="red")
                    return
                
                # 既に共有済みかチェック
                shared_users = asyncio.run(task_manager.get_shared_users_by_task(task_id))
                if any(shared_user[0] == user[0] for shared_user in shared_users):
                    error_label.configure(text="既にこのユーザーと共有済みです", text_color="red")
                    return
                
                asyncio.run(task_manager.share_with_users(task_id, user[0]))
                email_entry.delete(0, tk.END)
                error_label.configure(text="共有しました", text_color="green")
                refresh_share_list()
                
            except Exception as e:
                print(f"共有エラー: {e}")
                error_label.configure(text="共有に失敗しました", text_color="red")

        add_btn = tk.CTkButton(entry_frame, text="+", width=30, command=add_share)
        add_btn.pack(side="left", padx=5)

        # シェア一覧表示エリア
        list_frame = tk.CTkFrame(popup)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        # エラーメッセージ表示用ラベル（関数定義の前に作成）
        error_label = tk.CTkLabel(popup, text="", text_color="red")
        error_label.pack()

        def refresh_share_list():
            # エラー/成功メッセージをクリア
            error_label.configure(text="")
            
            for widget in list_frame.winfo_children():
                widget.destroy()
            try:
                # 指定されたタスクが共有されているユーザー一覧を取得
                shared_users = asyncio.run(task_manager.get_shared_users_by_task(task_id))
                if shared_users:
                    for user in shared_users:
                        row = tk.CTkFrame(list_frame)
                        row.pack(fill="x", pady=2)
                        # user = (user_id, email, name)
                        label = tk.CTkLabel(row, text=user[1], anchor="w")  # nameを表示
                        label.pack(side="left", padx=5)
                        del_btn = tk.CTkButton(
                            row,
                            text="削除",
                            width=40,
                            command=lambda uid=user[0]: remove_share(task_id, uid),
                        )
                        del_btn.pack(side="right", padx=5)
                else:
                    # 共有ユーザーがいない場合
                    no_share_label = tk.CTkLabel(list_frame, text="まだ誰とも共有していません")
                    no_share_label.pack(pady=10)
            except Exception as e:
                print(f"共有リスト取得エラー: {e}")
                # list_frame内に一時的なエラーラベルを作成
                temp_error_label = tk.CTkLabel(list_frame, text="共有リストの取得に失敗しました", text_color="red")
                temp_error_label.pack(pady=10)

        def remove_share(task_id, user_id):
            try:
                # DBから共有を削除
                asyncio.run(task_manager.unshare(task_id, user_id))
                error_label.configure(text="共有を解除しました", text_color="green")
                refresh_share_list()
            except Exception as e:
                print(f"共有解除エラー: {e}")
                error_label.configure(text="共有の解除に失敗しました", text_color="red")


        refresh_share_list()

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
