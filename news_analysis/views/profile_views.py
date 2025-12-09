from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from news_analysis.models import Comment, Collection, CollectionTag


@login_required
def profile(request):
    """个人空间首页"""
    # 计算评论数量和收藏数量
    comment_count = request.user.comments.filter(is_deleted=False).count()
    collection_count = request.user.collections.count()
    
    return render(request, 'profile/index.html', {
        'comment_count': comment_count,
        'collection_count': collection_count
    })


@login_required
def user_comments(request):
    """用户评论管理视图"""
    # 获取筛选条件
    search_query = request.GET.get('q', '')
    
    # 构建查询，获取当前用户的所有未删除评论
    query = Q(user=request.user, is_deleted=False)
    
    if search_query:
        query &= Q(content__icontains=search_query)
    
    # 获取评论列表，按时间倒序排列
    comments = Comment.objects.filter(query).order_by('-created_at')
    
    # 分页处理
    paginator = Paginator(comments, 10)
    page = request.GET.get('page', 1)
    
    try:
        comments_page = paginator.page(page)
    except PageNotAnInteger:
        comments_page = paginator.page(1)
    except EmptyPage:
        comments_page = paginator.page(paginator.num_pages)
    
    return render(request, 'profile/comments.html', {
        'comments': comments_page,
        'search_query': search_query
    })


@login_required
def edit_comment(request, pk):
    """编辑评论视图"""
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment.content = content
            comment.save()
            messages.success(request, '评论已更新！')
        else:
            messages.error(request, '评论内容不能为空。')
        return redirect('user_comments')
    
    return render(request, 'profile/edit_comment.html', {'comment': comment})


@login_required
def delete_comment(request, pk):
    """删除评论视图"""
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    comment.is_deleted = True
    comment.save()
    messages.success(request, '评论已删除！')
    return redirect('user_comments')


@login_required
def user_collections(request):
    """用户收藏管理视图"""
    # 获取筛选条件
    tag_id = request.GET.get('tag', '')
    sort_by = request.GET.get('sort', 'created_at')  # created_at 或 publish_time
    order = request.GET.get('order', 'desc')  # asc 或 desc
    
    # 构建查询
    query = Q(user=request.user)
    
    if tag_id:
        query &= Q(tags__id=tag_id)
    
    # 获取收藏列表
    collections = Collection.objects.filter(query).distinct()
    
    # 排序处理
    if sort_by == 'publish_time':
        if order == 'asc':
            collections = collections.order_by('news__publish_time')
        else:
            collections = collections.order_by('-news__publish_time')
    else:  # 默认按收藏时间排序
        if order == 'asc':
            collections = collections.order_by('created_at')
        else:
            collections = collections.order_by('-created_at')
    
    # 获取用户的所有收藏标签
    user_tags = CollectionTag.objects.filter(user=request.user).order_by('name')
    
    # 分页处理
    paginator = Paginator(collections, 10)
    page = request.GET.get('page', 1)
    
    try:
        collections_page = paginator.page(page)
    except PageNotAnInteger:
        collections_page = paginator.page(1)
    except EmptyPage:
        collections_page = paginator.page(paginator.num_pages)
    
    return render(request, 'profile/collections.html', {
        'collections': collections_page,
        'user_tags': user_tags,
        'selected_tag': tag_id,
        'sort_by': sort_by,
        'order': order
    })


@login_required
def add_collection_tag(request):
    """添加收藏标签"""
    if request.method == 'POST':
        tag_name = request.POST.get('tag_name', '').strip()
        if tag_name:
            # 检查标签是否已存在
            tag, created = CollectionTag.objects.get_or_create(
                user=request.user,
                name=tag_name
            )
            if created:
                messages.success(request, '标签创建成功！')
            else:
                messages.info(request, '该标签已存在。')
        else:
            messages.error(request, '标签名称不能为空。')
    return redirect('user_collections')


@login_required
def add_tag_to_collection(request, collection_id, tag_id):
    """为收藏添加标签"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    tag = get_object_or_404(CollectionTag, id=tag_id, user=request.user)
    
    if not collection.tags.filter(id=tag_id).exists():
        collection.tags.add(tag)
        messages.success(request, f'已添加标签 "{tag.name}"')
    
    return redirect('user_collections')


@login_required
def remove_tag_from_collection(request, collection_id, tag_id):
    """从收藏中移除标签"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    tag = get_object_or_404(CollectionTag, id=tag_id, user=request.user)
    
    if collection.tags.filter(id=tag_id).exists():
        collection.tags.remove(tag)
        messages.success(request, f'已移除标签 "{tag.name}"')
    
    return redirect('user_collections')


@login_required
def remove_collection(request, collection_id):
    """取消收藏"""
    collection = get_object_or_404(Collection, id=collection_id, user=request.user)
    collection.delete()
    messages.success(request, '已取消收藏！')
    return redirect('user_collections')
