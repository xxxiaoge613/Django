from django.urls import path
from .views import auth_views, news_views, visualization_views, profile_views

urlpatterns = [
    # 认证相关URL
    path('register/', auth_views.register, name='register'),
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    
    # 首页URL
    path('', news_views.home, name='home'),
    
    # 新闻相关URL
    path('news/', news_views.news_list, name='news_list'),
    path('news/<int:pk>/', news_views.news_detail, name='news_detail'),
    path('news/search/', news_views.news_search, name='news_search'),
    
    # 可视化相关URL
    path('dashboard/', visualization_views.dashboard, name='dashboard'),
    path('visualization/dashboard_data/', visualization_views.dashboard_data, name='dashboard_data'),
    path('sentiment-trend/', visualization_views.sentiment_trend, name='sentiment_trend'),
    path('platform-distribution/', visualization_views.platform_distribution, name='platform_distribution'),
    path('keyword-cloud/', visualization_views.keyword_cloud, name='keyword_cloud'),
    
    # 用户交互相关URL
    path('news/<int:pk>/collect/', news_views.collect_news, name='collect_news'),
    path('news/<int:pk>/comment/', news_views.add_comment, name='add_comment'),
    path('comment/<int:pk>/like/', news_views.like_comment, name='like_comment'),
    path('collections/', profile_views.user_collections, name='user_collections'),
    
    # 个人空间相关URL
    path('profile/', profile_views.profile, name='profile'),
    path('profile/comments/', profile_views.user_comments, name='user_comments'),
    path('profile/comments/<int:pk>/edit/', profile_views.edit_comment, name='edit_comment'),
    path('profile/comments/<int:pk>/delete/', profile_views.delete_comment, name='delete_comment'),
    path('profile/collections/', profile_views.user_collections, name='user_collections'),
    path('profile/collections/tag/add/', profile_views.add_collection_tag, name='add_collection_tag'),
    path('profile/collections/<int:collection_id>/tag/<int:tag_id>/add/', profile_views.add_tag_to_collection, name='add_tag_to_collection'),
    path('profile/collections/<int:collection_id>/tag/<int:tag_id>/remove/', profile_views.remove_tag_from_collection, name='remove_tag_from_collection'),
    path('profile/collections/<int:collection_id>/remove/', profile_views.remove_collection, name='remove_collection'),
]
