import re

from django.contrib.auth.backends import ModelBackend

from apps.users.models import User


class AuthMobile(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            if re.match(r'^1[3-9]\d{9}$', username):
                user = User.objects.get(mobile=username)
            else:
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return
        if user and user.check_password(password):
            return user
        else:
            return
