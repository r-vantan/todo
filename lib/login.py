from ..utils.db import auth_user

async def login(email, password):
    """
    Attempts to authenticate a user with the provided email and password.
    Args:
        email (str): The user's email address.
        password (str): The user's password.
    Returns:
        tuple:
            - bool: True if authentication is successful, False otherwise.
            - str: A message indicating the result of the login attempt.
            - user (Any or None): The authenticated user object if successful, None otherwise.
    """
    user = await auth_user(email, password)
    if user:
        return True, "ログイン成功", user
    return False, "メールとパスワードが一致しません。", None