from django.db import models


class BaseModel(models.Model):
    # 创建或添加对象时自动添加时间,修改或更新对象时不会更改时间
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    # 凡是对对象进行操作(创建/添加/修改/更新)时间都会随之改变
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True


class OAuthQQUser(BaseModel):
    # user是个外键,关联对应的用户
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    # qq发布的用户身份id
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)

    class Meta:
        db_table = 'tb_oauth_qq'
