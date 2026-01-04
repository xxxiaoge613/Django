from news_analysis.models import Comment, Like
from django.db.models import Q

class CommentRepository:
    """评论数据访问层，封装评论和点赞相关的数据库操作"""
    
    @staticmethod
    def get_comments_by_news_id(news_id, is_deleted=False):
        """根据新闻ID获取评论列表，默认获取未删除的评论"""
        return Comment.objects.filter(
            news_id=news_id,
            is_deleted=is_deleted,
            parent__isnull=True
        ).order_by('-created_at')
    
    @staticmethod
    def get_comment_by_id(comment_id):
        """根据ID获取评论"""
        return Comment.objects.get(id=comment_id)
    
    @staticmethod
    def create_comment(news, user, content, parent=None):
        """创建新评论"""
        return Comment.objects.create(
            news=news,
            user=user,
            content=content,
            parent=parent
        )
    
    @staticmethod
    def get_total_comments_by_news_id(news_id, is_deleted=False):
        """获取新闻的评论总数"""
        return Comment.objects.filter(
            news_id=news_id,
            is_deleted=is_deleted
        ).count()
    
    @staticmethod
    def is_liked_by_user(comment, user):
        """检查评论是否被用户点赞"""
        return Like.objects.filter(comment=comment, user=user).exists()
    
    @staticmethod
    def toggle_like(comment, user):
        """切换评论点赞状态"""
        like, created = Like.objects.get_or_create(comment=comment, user=user)
        
        if not created:
            like.delete()
            return False  # 返回False表示取消点赞
        return True  # 返回True表示成功点赞