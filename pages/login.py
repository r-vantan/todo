import tkinter as tk
from lib.login import login
from lib.session import save_session
import asyncio


class PlaceholderEntry(tk.Entry):
    def __init__(self, master, placeholder, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "grey"
        self.default_color = self["fg"] if self["fg"] else "black"
        self._is_password = "show" in kwargs
        self._is_placeholder_active = True  # プレースホルダー状態を明示的に管理

        if self._is_password:
            self.config(show="")

        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_color)

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event):
        if self._is_placeholder_active:
            self.delete(0, tk.END)
            self.config(fg=self.default_color)
            self._is_placeholder_active = False
            if self._is_password:
                self.config(show="*")

    def _on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
            self._is_placeholder_active = True
            if self._is_password:
                self.config(show="")

    def clear_to_placeholder(self):
        """値をクリアしてプレースホルダーに戻す"""
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_color)
        self._is_placeholder_active = True
        if self._is_password:
            self.config(show="")
        # フォーカスを外す
        if self.focus_get() == self:
            self.master.focus_set()
    
    def get_real_value(self):
        """プレースホルダーではない実際の値を取得"""
        if self._is_placeholder_active:
            return ""
        return self.get()


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # UIの構築
        label = tk.Label(self, text="ログイン")
        label.pack(pady=10)

        self.email_entry = PlaceholderEntry(self, "メールアドレス")
        self.email_entry.pack()

        self.password_entry = PlaceholderEntry(self, "パスワード", show="*")
        self.password_entry.pack()

        self.error_label = tk.Label(self, text="", fg="red")
        self.error_label.pack()

        # ログインボタン
        login_button = tk.Button(self, text="ログイン", command=self.handle_login)
        login_button.pack(pady=10)

        label = tk.Label(self, text="アカウントを登録", cursor="hand2")
        label.pack(pady=10)
        # ラベルにクリックイベントをバインドする
        label.bind("<Button-1>", lambda e: self.sign_up())

    def handle_login(self):
        email = self.email_entry.get_real_value()
        password = self.password_entry.get_real_value()

        if not email or not password:
            self.error_label.config(text="メールアドレスとパスワードを入力してください。")
            return

        result = asyncio.run(login(email, password))

        if result[0]:
            # ログイン成功後、Todoページに切り替える
            self.controller.show_frame("todo")
            self.error_label.config(text="")
            save_session(result[2])  # セッション情報を保存
            # パスワードをクリア
            self.password_entry.clear_to_placeholder()
        else:
            self.error_label.config(text=result[1])
            # ログイン失敗時もパスワードをクリア
            self.password_entry.clear_to_placeholder()

    def sign_up(self):
        # ページ遷移時にパスワードをクリア
        self.password_entry.clear_to_placeholder()
        # サインアップページの全フィールドをクリア
        signup_page = self.controller.frames.get("signup")
        if signup_page:
            signup_page.clear_all_fields()
        self.controller.show_frame("signup")
        # フォーカスをリセット
        self.controller.focus_set()