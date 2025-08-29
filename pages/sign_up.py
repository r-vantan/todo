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
        self.login_label.bind("<Button-1>", lambda e: self.back_to_login())

    def back_to_login(self):
        """ログイン画面に戻る時に全フィールドをクリア"""
        self.clear_all_fields()
        self.controller.show_frame("login")
        # フォーカスをリセット
        self.controller.focus_set()

    def clear_all_fields(self):
        """全フィールドをクリアしてプレースホルダーに戻す"""
        self.name_entry.clear_to_placeholder()
        self.email_entry.clear_to_placeholder()
        self.password_entry.clear_to_placeholder()
        self.error_label.config(text="")
        # フォーカスをリセット
        self.focus_set()

    def handle_sign_up(self):
        """
        登録ボタンがクリックされたときの処理
        """
        name = self.name_entry.get_real_value()
        email = self.email_entry.get_real_value()
        password = self.password_entry.get_real_value()

        if not name or not email or not password:
            self.error_label.config(text="全てのフィールドを入力してください。")
            return

        self.error_label.config(text="登録中...")
        result = asyncio.run(create_user(name, email, password))

        if result[0]:
            # 登録成功後、自動的にログイン
            self.error_label.config(text="登録成功！ログイン中...")
            login_result = asyncio.run(login(email, password))
            if login_result[0]:
                self.controller.show_frame("todo")
                self.error_label.config(text="")
                save_session(login_result[2])  # セッション情報を保存
                # 登録成功時に全フィールドをクリア
                self.clear_all_fields()
            else:
                self.error_label.config(
                    text="登録は成功しましたが、ログインに失敗しました。"
                )
                # ログイン失敗時も全フィールドをクリア
                self.clear_all_fields()
        else:
            self.error_label.config(text=result[1])
            # 登録失敗時も全フィールドをクリア
            self.clear_all_fields()
