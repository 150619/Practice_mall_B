from celery_tasks.main import celery_app
from celery_tasks.yuntongxun.send_sms import send_message


@celery_app.task(name='celery_send_sms')
def celery_send_sms(mobile, sms_code):
    result = send_message(mobile, sms_code)
    return result
