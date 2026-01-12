from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from news_analysis.forms.auth_forms import CustomUserCreationForm, CustomLoginForm

# 注册视图
def register(request):
    """用户注册视图"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 自动登录新注册用户
            login(request, user)
            messages.success(request, '注册成功！')
            return redirect('news_list')
        else:
            messages.error(request, '注册失败，请检查输入信息。')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

# 登录视图
def login_view(request):
    """用户登录视图"""
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # 处理记住我功能
                if remember:
                    # 设置长时间的会话过期时间（例如30天）
                    request.session.set_expiry(60 * 60 * 24 * 30)
                else:
                    # 使用默认的会话过期时间（浏览器关闭时过期）
                    request.session.set_expiry(0)
                messages.success(request, f'欢迎回来，{username}！')
                return redirect('news_list')
        messages.error(request, '登录失败，用户名或密码错误。')
    else:
        form = CustomLoginForm()
    
    return render(request, 'auth/login.html', {'form': form})

# 注销视图
@login_required
def logout_view(request):
    """用户注销视图"""
    logout(request)
    messages.success(request, '已成功注销。')
    return redirect('news_list')
