import tkinter as tk
import asyncio
from lib.sign_up import create_user
from lib.login import login
from lib.session import save_session


class PlaceholderEntry(tk.Entry):
    def __init__(self, master, placeholder, **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = "grey"
        self.default_color = self["fg"]
        self._is_password = "show" in kwargs

        if self._is_password:
            self.config(show="")

        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_color)

        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, event):
        if self["fg"] == self.placeholder_color:
            self.delete(0, tk.END)
            self.config(fg=self.default_color)
            if self._is_password:
                self.config(show="*")

    def _on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
            if self._is_password:
                self.config(show="")


class SignUpPage(tk.Frame):
    """
    新規登録ページ
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # UIの構築
        label = tk.Label(self, text="新規登録")
        label.pack(pady=10)

        self.name_entry = PlaceholderEntry(self, "名前")
        self.name_entry.pack()

        self.email_entry = PlaceholderEntry(self, "メールアドレス")
        self.email_entry.pack()

        self.password_entry = PlaceholderEntry(self, "パスワード", show="*")
        self.password_entry.pack()

        self.error_label = tk.Label(self, text="", fg="red")
        self.error_label.pack()

        # 登録ボタン
        sign_up_button = tk.Button(self, text="登録", command=self.handle_sign_up)
        sign_up_button.pack(pady=10)

        self.login_label = tk.Label(self, text="ログイン画面に戻る", cursor="hand2")
        self.login_label.pack()
        self.login_label.bind("<Button-1>", lambda e: self.controller.show_frame("login"))

    def handle_sign_up(self):
        """
        登録ボタンがクリックされたときの処理
        """
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        # プレースホルダーのテキストをチェック
        if name == "名前" or email == "メールアドレス" or password == "パスワード":
            self.error_label.config(text="全てのフィールドを入力してください。")
            return

        if not name or not email or not password:
            self.error_label.config(text="全てのフィールドを入力してください。")
            return

        asyncio.run(self._async_sign_up(name, email, password))

    async def _async_sign_up(self, name, email, password):
        """
        非同期のサインアップ処理
        """
        self.error_label.config(text="登録中...")
        result = await create_user(name, email, password)

        if result[0]:
            # 登録成功後、自動的にログイン
            self.error_label.config(text="登録成功！ログイン中...")
            login_result = await login(email, password)
            if login_result[0]:
                self.controller.show_frame("todo")
                self.error_label.config(text="")
                save_session(login_result[2])  # セッション情報を保存
            else:
                self.error_label.config(
                    text="登録は成功しましたが、ログインに失敗しました。"
                )
        else:
            self.error_label.config(text=result[1])
