from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# 新闻来源平台枚举
class PlatformChoice(models.TextChoices):
    QUANTUM_BIT = '量子位', '量子位'
    THIRTY_SIX_KR = '36kr', '36氪'

# 新闻表
class News(models.Model):
    title = models.CharField(max_length=255, verbose_name='新闻标题')
    content = models.TextField(verbose_name='新闻内容')
    publish_time = models.DateTimeField(verbose_name='发布时间')
    url = models.URLField(max_length=500, verbose_name='新闻链接', unique=True)
    platform = models.CharField(max_length=20, choices=PlatformChoice.choices, verbose_name='来源平台')
    source_id = models.CharField(max_length=100, verbose_name='平台内部ID', unique=True)
    author = models.CharField(max_length=100, blank=True, null=True, verbose_name='作者')
    read_count = models.IntegerField(default=0, verbose_name='阅读量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_valid = models.BooleanField(default=True, verbose_name='是否有效')
    is_ad = models.BooleanField(default=False, verbose_name='是否为广告')

    class Meta:
        verbose_name = '新闻'
        verbose_name_plural = '新闻列表'
        ordering = ['-publish_time']

    def __str__(self):
        return self.title

# 情感分析结果表
class SentimentAnalysis(models.Model):
    news = models.OneToOneField(News, on_delete=models.CASCADE, related_name='sentiment', verbose_name='关联新闻')
    sentiment_score = models.FloatField(verbose_name='情感得分')
    sentiment_type = models.CharField(max_length=10, verbose_name='情感类型')
    analysis_time = models.DateTimeField(auto_now_add=True, verbose_name='分析时间')

    class Meta:
        verbose_name = '情感分析结果'
        verbose_name_plural = '情感分析结果列表'

    def __str__(self):
        return f'{self.news.title} - {self.sentiment_type}'

# 评论表
class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments', verbose_name='关联新闻')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='评论用户')
    content = models.TextField(verbose_name='评论内容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评论时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name='父评论')
    is_deleted = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论列表'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'

# 点赞表
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name='点赞用户')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes', verbose_name='关联评论')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')

    class Meta:
        verbose_name = '点赞'
        verbose_name_plural = '点赞列表'
        unique_together = ('user', 'comment')

    def __str__(self):
        return f'{self.user.username} 点赞了 {self.comment.id}'

# 收藏表
class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections', verbose_name='收藏用户')
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='collections', verbose_name='收藏新闻')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        verbose_name = '收藏'
        verbose_name_plural = '收藏列表'
        unique_together = ('user', 'news')

    def __str__(self):
        return f'{self.user.username} 收藏了 {self.news.title[:20]}'

# 关键词表
class Keyword(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='keywords', verbose_name='关联新闻')
    keyword = models.CharField(max_length=50, verbose_name='关键词')
    weight = models.FloatField(default=0.0, verbose_name='权重')

    class Meta:
        verbose_name = '关键词'
        verbose_name_plural = '关键词列表'
        unique_together = ('news', 'keyword')

    def __str__(self):
        return f'{self.news.title[:20]} - {self.keyword}'

