import json
import os

SESSION_FILE = "session.json"

def save_session(user_data):
    """
    ユーザーセッション情報をファイルに保存する
    
    Args:
        user_data (tuple): ユーザー情報のタプル（id, name, email, password）
        
    Returns:
        None
    """
    if user_data:
        session_data = {
            "user_id": user_data[0],
            "user_name": user_data[1],
            "user_email": user_data[2],
            "is_logged_in": True
        }
    else:
        session_data = {
            "user_id": None,
            "user_name": None,
            "user_email": None,
            "is_logged_in": False
        }
    
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

def load_session():
    """
    セッション情報をファイルから読み込む
    
    Returns:
        dict: セッション情報の辞書、ファイルが存在しない場合は空のセッション情報
    """
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # ファイルが破損している場合は空のセッションを返す
            return get_empty_session()
    return get_empty_session()

def get_empty_session():
    """
    空のセッション情報を取得する
    
    Returns:
        dict: 空のセッション情報
    """
    return {
        "user_id": None,
        "user_name": None,
        "user_email": None,
        "is_logged_in": False
    }

def get_current_user_id():
    """
    現在ログイン中のユーザーIDを取得する
    
    Returns:
        int or None: ユーザーID、ログインしていない場合はNone
    """
    session = load_session()
    if session.get("is_logged_in", False):
        return session.get("user_id")
    return None

def get_current_user_info():
    """
    現在ログイン中のユーザー情報を取得する
    
    Returns:
        dict or None: ユーザー情報の辞書、ログインしていない場合はNone
    """
    session = load_session()
    if session.get("is_logged_in", False):
        return {
            "user_id": session.get("user_id"),
            "user_name": session.get("user_name"),
            "user_email": session.get("user_email")
        }
    return None

def is_logged_in():
    """
    ログイン状態を確認する
    
    Returns:
        bool: ログインしている場合True、していない場合False
    """
    session = load_session()
    return session.get("is_logged_in", False)

def logout():
    """
    ログアウト処理（セッション情報をnullに設定）
    
    Returns:
        None
    """
    save_session(None)

def clear_session():
    """
    セッションファイルを削除する
    
    Returns:
        None
    """
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
