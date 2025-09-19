import os
# macOSのIMKCエラーメッセージを抑制
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

import customtkinter as tk
from pages.login import LoginPage
from pages.todo import TodoPage
from pages.sign_up import SignUpPage
from lib.session import is_logged_in
import threading
from lib.reminder import reminder_loop
import asyncio


class App(tk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TODOアプリ")
        self.geometry("800x600")
        self.minsize(600, 400)  # 最小サイズを設定
        self.maxsize(1600, 1200)  # 最大サイズを設定

        # ページを格納するコンテナフレーム
        self.container = tk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        # ページのインスタンスを作成
        for F in [LoginPage, TodoPage, SignUpPage]:
            page_name = F.__name__.replace("Page", "").lower()
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # コンテナのグリッド設定
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # 初期ページを決定（セッション状態に基づく）
        if is_logged_in():
            self.show_frame("todo")
        else:
            self.show_frame("login")

    def show_frame(self, page_name):
        """指定したページを最前面に表示する"""
        frame = self.frames[page_name]
        frame.tkraise()
        # フォーカスをリセットして、前のページのフォーカス状態を無効化
        frame.focus_set()
        # 少し待ってから再度フォーカスをリセット（確実にするため）
        self.after(1, lambda: frame.focus_set())


if __name__ == "__main__":
    tk.set_appearance_mode("Dark")
    tk.set_default_color_theme("blue")
    app = App()

    def run_reminder_loop():
        asyncio.run(reminder_loop())

    threading.Thread(target=run_reminder_loop, daemon=True).start()
    app.mainloop()
