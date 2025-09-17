# ToDoアプリ
---

## 使用技術

- Tkinter
- SQLite

## 機能

1. タスク追加
2. タスク削除
3. タスク一覧
4. タスク完了/未完了マーク
5. タスク編集
6. 締め切り日
7. 優先度設定
8. タスクタグ付け
9. タスク検索
10. タスクリマインダー
11. タスク並び替え
12. タスク共有
13. ユーザーログイン

## データベース設計

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

---