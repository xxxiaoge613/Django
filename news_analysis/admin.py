from django.contrib import admin
from .models import (
    News,
    SentimentAnalysis,
    Comment,
    Like,
    Collection,
    Keyword
)

# 自定义新闻管理界面
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'platform', 'publish_time', 'is_valid')
    search_fields = ('title', 'content', 'author')
    list_filter = ('platform', 'is_valid', 'publish_time')
    date_hierarchy = 'publish_time'
    ordering = ('-publish_time',)

# 自定义情感分析管理界面
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = ('news_title', 'sentiment_score', 'sentiment_type', 'analysis_time')
    search_fields = ('news__title', 'sentiment_type')
    list_filter = ('sentiment_type', 'analysis_time')
    date_hierarchy = 'analysis_time'
    ordering = ('-analysis_time',)
    
    def news_title(self, obj):
        return obj.news.title[:50] + '...' if len(obj.news.title) > 50 else obj.news.title
    news_title.short_description = '新闻标题'

# 自定义评论管理界面
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'news_title', 'content_preview', 'created_at', 'is_deleted')
    search_fields = ('user__username', 'content', 'news__title')
    list_filter = ('is_deleted', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def news_title(self, obj):
        return obj.news.title[:30] + '...' if len(obj.news.title) > 30 else obj.news.title
    news_title.short_description = '新闻标题'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '评论内容'

# 自定义点赞管理界面
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'comment_preview', 'created_at')
    search_fields = ('user__username', 'comment__content')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def comment_preview(self, obj):
        return obj.comment.content[:30] + '...' if len(obj.comment.content) > 30 else obj.comment.content
    comment_preview.short_description = '评论内容'

# 自定义收藏管理界面
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'news_title', 'created_at')
    search_fields = ('user__username', 'news__title')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    def news_title(self, obj):
        return obj.news.title[:30] + '...' if len(obj.news.title) > 30 else obj.news.title
    news_title.short_description = '新闻标题'

# 自定义关键词管理界面
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('news_title', 'keyword', 'weight')
    search_fields = ('news__title', 'keyword')
    list_filter = ('keyword',)
    ordering = ('-weight',)
    
    def news_title(self, obj):
        return obj.news.title[:30] + '...' if len(obj.news.title) > 30 else obj.news.title
    news_title.short_description = '新闻标题'

# 注册所有模型
admin.site.register(News, NewsAdmin)
admin.site.register(SentimentAnalysis, SentimentAnalysisAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Keyword, KeywordAdmin)

# 自定义admin站点信息
admin.site.site_header = '财经新闻分析平台后台管理'
admin.site.site_title = '财经新闻分析平台'
admin.site.index_title = '欢迎使用财经新闻分析平台后台'
