from news_analysis.repositories.news_repository import NewsRepository
from news_analysis.repositories.comment_repository import CommentRepository
from news_analysis.repositories.collection_repository import CollectionRepository
from news_analysis.services.keyword_service import KeywordService

class NewsService:
    """新闻服务层，封装新闻相关的业务逻辑"""
    
    def __init__(self):
        self.news_repo = NewsRepository()
        self.comment_repo = CommentRepository()
        self.collection_repo = CollectionRepository()
        self.keyword_service = KeywordService()
    
    def get_news_detail(self, news_id, user=None):
        """获取新闻详情，包括评论、收藏状态、相关新闻等"""
        # 1. 获取新闻基本信息并增加阅读量
        news = self.news_repo.increase_read_count(news_id)
        
        # 2. 获取评论列表
        comments = self.comment_repo.get_comments_by_news_id(news_id)
        
        # 3. 获取评论总数
        total_comments = self.comment_repo.get_total_comments_by_news_id(news_id)
        
        # 4. 检查用户是否收藏该新闻
        is_collected = False
        if user and user.is_authenticated:
            is_collected = self.collection_repo.is_collected_by_user(news, user)
        
        # 5. 获取相关推荐新闻
        related_news = self.news_repo.get_related_news(news_id)
        
        # 6. 提取关键词
        hot_keywords = self.keyword_service.extract_keywords(news.title + ' ' + news.content)
        
        # 7. 检查用户是否点赞了每条评论
        if user and user.is_authenticated:
            for comment in comments:
                comment.is_liked = self.comment_repo.is_liked_by_user(comment, user)
                # 检查每条回复是否被用户点赞
                for reply in comment.replies.all():
                    if not reply.is_deleted:
                        reply.is_liked = self.comment_repo.is_liked_by_user(reply, user)
        
        return {
            'news': news,
            'comments': comments,
            'total_comments': total_comments,
            'is_collected': is_collected,
            'related_news': related_news,
            'hot_keywords': hot_keywords
        }
    
    def get_news_list(self, platform=None, sentiment=None, search_query=None, search_mode='keyword', page=1, page_size=10):
        """获取新闻列表，支持筛选和分页"""
        news_list = self.news_repo.get_news_list(
            platform=platform,
            sentiment=sentiment,
            search_query=search_query,
            search_mode=search_mode,
            page=page,
            page_size=page_size
        )
        
        available_platforms = self.news_repo.get_available_platforms()
        
        return {
            'news_list': news_list,
            'available_platforms': available_platforms
        }
    
    def toggle_collection(self, news_id, user):
        """切换新闻收藏状态"""
        news = self.news_repo.get_news_by_id(news_id)
        return self.collection_repo.toggle_collection(news, user)
    
    def get_news_by_id(self, news_id):
        """根据ID获取新闻"""
        return self.news_repo.get_news_by_id(news_id)
    
    def add_comment(self, news_id, user, content, parent_id=None):
        """添加评论"""
        news = self.news_repo.get_news_by_id(news_id)
        parent = None
        
        if parent_id:
            parent = self.comment_repo.get_comment_by_id(parent_id)
        
        return self.comment_repo.create_comment(news, user, content, parent)
    
    def toggle_like(self, comment_id, user):
        """切换评论点赞状态"""
        comment = self.comment_repo.get_comment_by_id(comment_id)
        return self.comment_repo.toggle_like(comment, user)
    
    def get_comment_by_id(self, comment_id):
        """根据ID获取评论"""
        return self.comment_repo.get_comment_by_id(comment_id)
    
    def get_total_comments_by_news_id(self, news_id):
        """获取新闻的评论总数"""
        return self.comment_repo.get_total_comments_by_news_id(news_id)
    
    def get_user_collections(self, user, page=1, page_size=10):
        """获取用户收藏列表"""
        return self.collection_repo.get_collections_by_user(user, page, page_size)
