from news_analysis.models import Collection, CollectionTag

class CollectionRepository:
    """收藏数据访问层，封装收藏和标签相关的数据库操作"""
    
    @staticmethod
    def is_collected_by_user(news, user):
        """检查新闻是否被用户收藏"""
        return Collection.objects.filter(news=news, user=user).exists()
    
    @staticmethod
    def toggle_collection(news, user):
        """切换新闻收藏状态"""
        collection, created = Collection.objects.get_or_create(news=news, user=user)
        
        if not created:
            collection.delete()
            return False  # 返回False表示取消收藏
        return True  # 返回True表示成功收藏
    
    @staticmethod
    def get_collections_by_user(user, page=1, page_size=10):
        """获取用户的收藏列表"""
        return Collection.objects.filter(user=user).order_by('-created_at')
    
    @staticmethod
    def get_collection_tags_by_user(user):
        """获取用户的收藏标签列表"""
        return CollectionTag.objects.filter(user=user)
    
    @staticmethod
    def create_collection_tag(name, user):
        """创建收藏标签"""
        return CollectionTag.objects.create(name=name, user=user)
