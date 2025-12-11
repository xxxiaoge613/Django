from django.http import JsonResponse
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin
import time
from collections import defaultdict

# 存储IP地址的注册请求记录
# 格式：{ip: [timestamp1, timestamp2, ...]}
register_requests = defaultdict(list)
# 时间窗口（秒）
TIME_WINDOW = 60
# 时间窗口内允许的最大请求数
MAX_REQUESTS = 5

class RegisterRateLimitMiddleware(MiddlewareMixin):
    """注册频率限制中间件，防止恶意注册"""
    
    def process_request(self, request):
        """处理请求，检查注册频率"""
        # 只对注册页面的POST请求进行限制
        if request.path == '/register/' and request.method == 'POST':
            # 获取客户端IP地址
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
            
            # 获取当前时间戳
            current_time = time.time()
            
            # 清理过期的请求记录
            register_requests[ip] = [timestamp for timestamp in register_requests[ip] 
                                     if current_time - timestamp < TIME_WINDOW]
            
            # 检查请求频率是否超过限制
            if len(register_requests[ip]) >= MAX_REQUESTS:
                # 如果是AJAX请求，返回JSON响应
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'error',
                        'message': f'注册请求过于频繁，请在{int(TIME_WINDOW - (current_time - register_requests[ip][0])) + 1}秒后重试'
                    }, status=429)
                # 否则返回HTML页面
                else:
                    from django.contrib.auth.forms import UserCreationForm
                    form = UserCreationForm()
                    return render(request, 'auth/register.html', {
                        'form': form,
                        'rate_limit_error': f'注册请求过于频繁，请在{int(TIME_WINDOW - (current_time - register_requests[ip][0])) + 1}秒后重试'
                    }, status=429)
            
            # 记录当前请求
            register_requests[ip].append(current_time)
        
        return None