from utils.db import create_user

async def create_user(name, email, password):
    """
    Creates a new user with the provided name, email, and password.
    Args:
        name (str): The user's name.
        email (str): The user's email address.
        password (str): The user's password.
    Returns:
        tuple:
            - bool: True if user creation is successful, False otherwise.
            - str: A message indicating the result of the user creation attempt.
    """
    try:
        await create_user(name, email, password)
        return True, "ユーザー登録が成功しました。"
    except Exception as e:
        return False, f"ユーザー登録に失敗しました: {str(e)}"