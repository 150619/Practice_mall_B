import random

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from apps.verifications.libs.captcha.captcha import captcha
from apps.verifications.libs.yuntongxun.send_sms import send_message


class ImageCodes(View):
    def get(self, request, uuid):
        # 生成图形验证码
        text, image = captcha.generate_captcha()
        # 保存图形验证码,连接redis数据库(别名),redis数据库添加(字符串类型)
        redis_connect = get_redis_connection('verify_code')
        redis_connect.setex(f'code_{uuid}', 300, text)
        return HttpResponse(image, content_type='image/jpg')


class SmsCodes(View):
    def get(self, request, mobile):
        search_dict = request.GET
        image_code = search_dict.get('image_code')
        image_code_id = search_dict.get('image_code_id')
        if not all([image_code, image_code_id]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        redis_connect = get_redis_connection('verify_code')
        # 从redis数据库获取图形验证码
        b_real_image_code = redis_connect.get(f'code_{image_code_id}')
        if not b_real_image_code:
            return JsonResponse({'code': 400, 'errmsg': '图形验证码已过期'})
        # 获取后从redis数据库中删除图形验证码,避免重复使用
        redis_connect.delete(f'code_{image_code_id}')
        # redis中获取的数据是二进制需要转换成字符串
        real_image_code = b_real_image_code.decode()
        # 全部转换为小写,相等生成短信验证码
        if image_code.lower() == real_image_code.lower():
            sms_code = '%06d' % random.randint(0, 999999)
            send_flag = redis_connect.get(f'send_flag{mobile}')
            # 过期值存在说明这个手机发送短信过于频繁
            if send_flag:
                return JsonResponse({'code': 400, 'errmsg': '请勿频繁发送短信'})
            pl = redis_connect.pipeline()
            # 将短信验证码储存到redis数据库
            pl.setex(name=mobile, time=60, value=sms_code)
            # 发送完成后设置一个60秒的过期值
            pl.setex(name=f'send_flag{mobile}', time=60, value=1)
            pl.execute()
            send_message(mobile, sms_code)
            print(sms_code)
            return JsonResponse({'code': 0, 'errmsg': '短信验证码发送成功'})
        # 不相等返回错误信息
        else:
            return JsonResponse({'code': 400, 'errmsg': '图形输入验证码错误'})
