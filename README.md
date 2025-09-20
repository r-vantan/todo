# 📋 ToDoアプリ

> 高機能なデスクトップタスク管理アプリケーション

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Tkinter](https://img.shields.io/badge/UI-CustomTkinter-green.svg)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 クイックスタート

```bash
# リポジトリをクローン
git clone https://github.com/r-vantan/todo.git
cd todo

# 仮想環境を作成
python -m venv .venv

# 仮想環境を有効化
# macOS/Linux:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# データベースを初期化
python init.py

# アプリケーションを起動
python main.py
```

## ✨ 主な機能

### 📝 基本機能
- **タスク管理**: 追加・削除・編集・完了状態の切り替え
- **一覧表示**: 見やすいリスト形式でタスクを表示
- **リアルタイム更新**: 即座に変更が反映される直感的なUI

### 🎯 高度な機能
- **⏰ 締切日設定**: カレンダーから簡単に期限を設定
- **🔢 優先度管理**: 5段階の優先度で重要なタスクを整理
- **🏷️ タグシステム**: カスタムタグでタスクを分類・フィルタリング
- **🔍 検索機能**: キーワードでタスクを瞬時に検索
- **🔔 リマインダー**: 指定時間に通知でタスクを忘れない
- **📊 並び替え**: 作成日・期限・優先度・名前で自由にソート
- **👥 共有機能**: 他のユーザーとタスクを共有
- **🔐 ユーザー認証**: 安全なログイン・アカウント管理

## 💻 使用技術

| 技術 | 用途 | バージョン |
|------|------|------------|
| **Python** | メイン言語 | 3.12+ |
| **CustomTkinter** | UI | latest |
| **SQLite** | データベース | 3.x |
| **aiosqlite** | 非同期DB操作 | latest |
| **bcrypt** | パスワード暗号化 | latest |
| **tkcalendar** | 日付選択UI | latest |

## 🏗️ アーキテクチャ

```
todo/
├── main.py              # アプリケーションエントリーポイント
├── config.py            # 設定ファイル
├── init.py              # データベース初期化
├── requirements.txt     # Python依存関係
├── pages/               # UIページ
│   ├── login.py         # ログインページ
│   ├── sign_up.py       # サインアップページ
│   └── todo.py          # メインTodoページ
├── lib/                 # ビジネスロジック
│   ├── users.py         # ユーザー管理
│   ├── tasks.py         # タスク管理
│   ├── tags.py          # タグ管理
│   ├── reminder.py      # リマインダー機能
│   └── session.py       # セッション管理
├── utils/               # ユーティリティ
│   ├── db.py            # データベース接続
│   └── db_init.py       # DB初期化スクリプト
└── static/              # 静的ファイル（アイコン等）
```

## 📋 詳細セットアップガイド

### 前提条件
- Python 3.12以上がインストールされていること
- Git がインストールされていること
- ターミナル/コマンドプロンプトが使用できること

### ステップ1: リポジトリのクローン
```bash
# プロジェクトをダウンロード
git clone https://github.com/r-vantan/todo.git
cd todo
```

### ステップ2: 仮想環境の構築
```bash
# 仮想環境を作成
python -m venv .venv

# 仮想環境を有効化
# macOS/Linux の場合:
source .venv/bin/activate

# Windows の場合:
.venv\Scripts\activate

# 仮想環境が有効になったことを確認
which python  # macOS/Linux
where python   # Windows
```

### ステップ3: 依存関係のインストール
```bash
# pip を最新版にアップデート
pip install --upgrade pip

# プロジェクトの依存関係をインストール
pip install -r requirements.txt

# インストールされたパッケージを確認
pip list
```

### ステップ4: データベースの初期化
```bash
# データベースとテーブルを作成
python init.py

# データベースファイルが作成されたことを確認
ls -la *.db  # macOS/Linux
dir *.db     # Windows
```

### ステップ5: アプリケーションの起動
```bash
# アプリケーションを起動
python main.py
```

### トラブルシューティング

#### Python バージョンエラー
```bash
# Python バージョンを確認
python --version

# Python 3.12+ が必要です
# インストールしていない場合は公式サイトからダウンロード
```

#### 依存関係インストールエラー
```bash
# キャッシュをクリアして再インストール
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

#### データベースエラー
```bash
# 既存のデータベースを削除して再作成
rm todo.db
python init.py
```

#### 仮想環境のトラブル
```bash
# 仮想環境を削除して再作成
rm -rf .venv  # macOS/Linux
rmdir /s .venv  # Windows

python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### セキュリティ機能

#### パスワードハッシュ化
```python
import bcrypt

# パスワードをハッシュ化
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# パスワードを検証
is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed)
```

#### SQLインジェクション対策
```python
# パラメータ化クエリを使用
await cursor.execute(
    "SELECT * FROM tasks WHERE user = ? AND name LIKE ?",
    (user_id, f"%{keyword}%")
)
```

### パフォーマンス最適化

#### 非同期処理
- `aiosqlite` による非ブロッキングDB操作
- バックグラウンドでのリマインダー監視
- UIの応答性を保つ非同期タスク実行

## 📊 データベース設計詳細

#### users
| カラム名    | 型         | 制約         | 説明           |
|-------------|------------|--------------|----------------|
| id          | INTEGER    | PRIMARY KEY  | ユーザーID     |
| name        | TEXT       | NOT NULL     | ユーザー名     |
| email       | TEXT       | UNIQUE       | メールアドレス |
| password    | TEXT       | NOT NULL     | ハッシュ化パスワード |

#### task_shares
| カラム名   | 型       | 制約                | 説明               |
|------------|----------|---------------------|--------------------|
| id         | INTEGER  | PRIMARY KEY         | 共有ID             |
| task_id    | INTEGER  | FOREIGN KEY         | tasks(id)          |
| user_id    | INTEGER  | FOREIGN KEY         | users(id) 共有相手 |

#### users
| カラム名    | 型         | 制約         | 説明           |
|-------------|------------|--------------|----------------|
| id          | INTEGER    | PRIMARY KEY  | ユーザーID     |
| name        | TEXT       | NOT NULL     | ユーザー名     |
| email       | TEXT       | UNIQUE       | メールアドレス |
| password    | TEXT       | NOT NULL     | ハッシュ化パスワード |

#### task_shares
| カラム名   | 型       | 制約                | 説明               |
|------------|----------|---------------------|--------------------|
| id         | INTEGER  | PRIMARY KEY         | 共有ID             |
| task_id    | INTEGER  | FOREIGN KEY         | tasks(id)          |
| user_id    | INTEGER  | FOREIGN KEY         | users(id) 共有相手 |

#### tasks
| カラム名      | 型         | 制約                | 説明                   |
|---------------|------------|---------------------|------------------------|
| id            | INTEGER    | PRIMARY KEY         | タスクID               |
| user          | INTEGER    | FOREIGN KEY         | users(id) タスク所有者 |
| shared_with   | TEXT       |                     | 共有ユーザーIDリスト   |
| is_done       | BOOLEAN    | DEFAULT 0           | 完了フラグ             |
| name          | TEXT       | NOT NULL            | タスク名               |
| description   | TEXT       |                     | 詳細                   |
| tag           | INTEGER    | FOREIGN KEY         | tags(id) タグID        |
| deadline      | DATETIME   |                     | 締め切り日             |
| priority      | INTEGER    | DEFAULT 0           | 優先度                 |
| created_at    | DATETIME   | DEFAULT CURRENT_TIMESTAMP | 作成日時         |
| updated_at    | DATETIME   |                     | 更新日時               |
| completed_at  | DATETIME   |                     | 完了日時               |

#### tags
| カラム名 | 型      | 制約                           | 説明      |
|----------|---------|--------------------------------|-----------|
| id       | INTEGER | PRIMARY KEY                    | タグID    |
| user     | INTEGER | FOREIGN KEY (users.id)         | 所有ユーザーID |
| name     | TEXT    | NOT NULL, UNIQUE(user, name)   | タグ名    |
| color    | TEXT    |                                | タグ色    |

#### reminders
| カラム名    | 型         | 制約                | 説明               |
|-------------|------------|---------------------|--------------------|
| id          | INTEGER    | PRIMARY KEY         | リマインダーID     |
| task_id     | INTEGER    | FOREIGN KEY         | tasks(id)          |
| remind_at   | DATETIME   | NOT NULL            | リマインド日時     |
| is_sent     | BOOLEAN    | DEFAULT 0           | 送信済みフラグ     |