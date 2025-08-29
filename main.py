import os
# macOSのIMKCエラーメッセージを抑制
os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

import tkinter as tk
from pages.login import LoginPage
from pages.todo import TodoPage
from pages.sign_up import SignUpPage
from lib.session import is_logged_in


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TODOアプリ")
        self.geometry("400x300")

        # ページを格納するコンテナフレーム
        self.container = tk.Frame(self)
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
    app = App()
    app.mainloop()
