import json
import re

from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.views import View
from django_redis import get_redis_connection

from apps.users.models import User


class RegisterName(View):
    # 解析路径参数
    def get(self, request, username):
        # 从数据库中查询数据
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': '0', 'errmsg': 'ok', 'count': count})


class RegisterMobile(View):
    def get(self, request, mobile):
        # 从数据库中查询数据
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': '0', 'errmsg': 'ok', 'count': count})


class Register(View):
    def post(self, request):
        # 解析请求体参数
        # json_bytes = request.body
        # json_str = json_bytes.decode()
        json_dict = json.loads(request.body)
        # 获取username
        username = json_dict.get('username')
        # 获取password和password2
        password = json_dict.get('password')
        password2 = json_dict.get('password2')
        # 获取mobile
        mobile = json_dict.get('mobile')
        # 获取sms_code
        sms_code = json_dict.get('sms_code')
        # 获取allow
        allow = json_dict.get('allow')
        # 判断必传参数是否全部存在,allow不用校验
        if not all([username, password, password2, mobile, sms_code]):
            return JsonResponse({'code': '400', 'errmsg': '缺少必传参数'})
        # 判断username的格式
        if not re.match(r'[a-zA-Z0-9_-]{5,20}', username):
            return JsonResponse({'code': '400', 'errmsg': '用户名格式错误'})
        # 判断数据库中是否已经存在一个username
        count = User.objects.filter(username=username).count()
        # 存在返回错误码
        if count > 0:
            return JsonResponse({'code': '400', 'errmsg': '用户名已存在'})
        # 判断密码格式
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return JsonResponse({'code': '400', 'errmsg': '密码格式错误'})
        # 判断password和password2是否相等,不相等返回错误码
        if password != password2:
            return JsonResponse({'code': '400', 'errmsg': '两次输入的密码不一致'})
        # 判断手机号格式
        if not re.match(r'1[3-9]\d{9}', mobile):
            return JsonResponse({'code': '400', 'errmsg': '手机号格式不正确'})
        # 判断手机号是否存在
        count = User.objects.filter(mobile=mobile).count()
        if count > 0:
            return JsonResponse({'code': '400', 'errmsg': '手机号已存在'})
        # 与redis中储存的验证码做对比
        redis_connect = get_redis_connection('verify_code')
        real_sms_code_b = redis_connect.get(f'{mobile}')
        # 判断redis数据库短信验证码是否过期
        if real_sms_code_b:
            real_sms_code = real_sms_code_b.decode()
            # 如果不相等返回错误码
            if real_sms_code != sms_code:
                return JsonResponse({'code': '400', 'errmsg': '短信验证码错误'})
        else:
            return JsonResponse({'code': '400', 'errmsg': '短信验证码不存在或已过期,请重新获取'})
        # 不为True返回错误码
        if not allow:
            return JsonResponse({'code': '400', 'errmsg': '请同意用户协议'})
        # 将获取到的数据保存到数据库,直接使用create会导致authenticate无法认证,且密码是明文储存到数据库
        # user = User.objects.create(username=username, password=password, mobile=mobile)
        user = User.objects.create_user(username=username, password=password, mobile=mobile)
        # 登录状态保持
        login(request, user)
        return JsonResponse({'code': '0', 'errmsg': 'ok'})


class Login(View):
    def post(self, request):
        json_dict = json.loads(request.body)
        # 获取参数
        username = json_dict.get('username')
        password = json_dict.get('password')
        remembered = json_dict.get('remembered')
        # 判断参数是否全部存在remembered不用校验
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})

        # 从数据库获取数据(使用filter返回的是QuerySet不方便做状态保持)
        # user = User.objects.filter(username=username, password=password)

        # 判断用户输入的账号是否是手机号
        # if re.match(r'^1[3-9]\d{9}$', username):
        # 将USERNAME_FIELD指定为mobile字段
        # User.USERNAME_FIELD = 'mobile'
        # else:
        # 将USERNAME_FIELD指定为username字段
        # User.USERNAME_FIELD = 'username'

        # 判断用户输入的账号是否是手机号

        # 验证用户名和密码
        user = authenticate(request=None, username=username, password=password)

        if not user:
            return JsonResponse({'code': 400, 'errmsg': '用户名或密码错误'})
        # 登录状态保持
        login(request, user)
        if remembered:
            request.session.set_expiry(None)
        else:
            request.session.set_expiry(0)
        # 后端设置cookie,前端获取cookie,使页面可以展示用户名
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', user.username, max_age=3600 * 24 * 14)
        return response
