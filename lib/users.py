from utils.db import (
    create_user,
    get_user_by_email,
    get_user_by_id
)

class UserManager:
    """ユーザー管理のためのライブラリクラス"""
    
    @staticmethod
    async def create(name, email, password_hash):
        """新しいユーザーを作成する"""
        await create_user(name, email, password_hash)
    
    @staticmethod
    async def get_by_email(email):
        """メールアドレスでユーザーを取得する"""
        return await get_user_by_email(email)
    
    @staticmethod
    async def get_by_id(user_id):
        """IDでユーザーを取得する"""
        return await get_user_by_id(user_id)