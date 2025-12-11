from django.shortcuts import render, redirect, reverse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from news_analysis.forms.auth_forms import CustomUserCreationForm

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
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'欢迎回来，{username}！')
                return redirect('news_list')
        messages.error(request, '登录失败，用户名或密码错误。')
    else:
        form = AuthenticationForm()
    
    return render(request, 'auth/login.html', {'form': form})

# 注销视图
@login_required
def logout_view(request):
    """用户注销视图"""
    logout(request)
    messages.success(request, '已成功注销。')
    return redirect('news_list')
