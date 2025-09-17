from utils.db import (
    create_tag,
    get_tags_by_user,
    get_tag_by_id,
    delete_tag
)

class TagManager:
    """タグ管理のためのライブラリクラス"""
    
    @staticmethod
    async def create(user_id, name):
        """新しいタグを作成する"""
        await create_tag(user_id, name)
    
    @staticmethod
    async def get_by_user(user_id):
        """ユーザーのタグ一覧を取得する"""
        return await get_tags_by_user(user_id)
    
    @staticmethod
    async def get_by_id(tag_id):
        """IDでタグを取得する"""
        return await get_tag_by_id(tag_id)
    
    @staticmethod
    async def delete(tag_id):
        """タグを削除する"""
        await delete_tag(tag_id)