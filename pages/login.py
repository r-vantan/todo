import customtkinter as tk
from lib.login import login
from lib.session import save_session
import asyncio


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


class LoginPage(tk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # UIの構築
        label = tk.CTkLabel(self, text="ログイン")
        label.pack(pady=5)

        self.email_entry = PlaceholderCTkEntry(self, "メールアドレス")
        self.email_entry.pack(pady=5)

        self.password_entry = PlaceholderCTkEntry(self, "パスワード", show="*")
        self.password_entry.pack(pady=5)

        self.error_label = tk.CTkLabel(self, text="", text_color="red")
        self.error_label.pack()

        # ログインボタン
        login_button = tk.CTkButton(self, text="ログイン", command=self.handle_login)
        login_button.pack(pady=5)

        sign_up_label = tk.CTkLabel(self, text="アカウントを登録", cursor="hand2")
        sign_up_label.pack(pady=5)
        # ラベルにクリックイベントをバインドする
        sign_up_label.bind("<Button-1>", lambda e: self.sign_up())

    def handle_login(self):
        email = self.email_entry.get_real_value()
        password = self.password_entry.get_real_value()

        if not email or not password:
            self.error_label.configure(text="メールアドレスとパスワードを入力してください。")
            return

        result = asyncio.run(login(email, password))

        if result[0]:
            # ログイン成功後、Todoページに切り替える
            self.controller.show_frame("todo")
            self.error_label.configure(text="")
            save_session(result[2])  # セッション情報を保存
            # パスワードをクリア
            self.password_entry.clear_to_placeholder()
        else:
            self.error_label.configure(text=result[1])
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