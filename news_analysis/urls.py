from django.urls import path
from .views import auth_views, news_views, visualization_views

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
    path('collections/', news_views.user_collections, name='user_collections'),
]
