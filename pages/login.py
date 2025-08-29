import tkinter as tk
from lib.login import login
from lib.session import save_session
import asyncio


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # UIの構築
        label = tk.Label(self, text="ログイン")
        label.pack(pady=10)

        self.email_entry = tk.Entry(self)
        self.email_entry.pack()

        self.password_entry = tk.Entry(self, show="*")
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
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            self.error_label.config(text="メールアドレスとパスワードを入力してください。")
            return

        result = asyncio.run(login(email, password))

        if result[0]:
            # ログイン成功後、Todoページに切り替える
            self.controller.show_frame("todo")
            self.error_label.config(text="")
            save_session(result[2])  # セッション情報を保存
        else:
            self.error_label.config(text=result[1])

    def sign_up(self):
        self.controller.show_frame("signup")