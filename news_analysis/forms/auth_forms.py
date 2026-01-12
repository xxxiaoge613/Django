from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class CustomUserCreationForm(UserCreationForm):
    """自定义用户注册表单，添加密码复杂度验证"""
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
    
    def clean_password1(self):
        """验证密码复杂度"""
        password1 = self.cleaned_data.get('password1')
        
        # 密码长度至少8位
        if len(password1) < 8:
            raise ValidationError("密码长度至少为8位")
        
        # 密码必须包含字母和数字
        if not re.search(r'[A-Za-z]', password1):
            raise ValidationError("密码必须包含字母")
        if not re.search(r'[0-9]', password1):
            raise ValidationError("密码必须包含数字")
        
        # 密码可以包含特殊字符
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError("密码必须包含特殊字符")
        
        return password1
    
    def clean_username(self):
        """验证用户名"""
        username = self.cleaned_data.get('username')
        
        # 用户名长度限制
        if len(username) < 3 or len(username) > 20:
            raise ValidationError("用户名长度必须在3到20个字符之间")
        
        # 用户名只能包含字母、数字和下划线
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            raise ValidationError("用户名只能包含字母、数字和下划线")
        
        return username

class CustomLoginForm(AuthenticationForm):
    """自定义登录表单，添加记住我功能"""
    remember = forms.BooleanField(required=False, label='记住我')