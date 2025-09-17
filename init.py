import os
import subprocess

# todo.dbファイルを同じディレクトリに作成
db_path = os.path.join(os.path.dirname(__file__), 'todo.db')
if not os.path.exists(db_path):
    open(db_path, 'w').close()

# ./utils/db_init.py を実行
utils_path = os.path.join(os.path.dirname(__file__), 'utils', 'db_init.py')
subprocess.run(['python', utils_path])