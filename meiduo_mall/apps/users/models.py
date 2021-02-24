from django.contrib.auth.models import AbstractUser
from django.db import models


# 自定义用户模型类,重写模型类,继承自AbstractUser
class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')

    class Meta:
        # 数据表名字
        db_table = 'tb_users'
        # 数据表的别名
        verbose_name = '用户'
        # 数据表的其它别名
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
