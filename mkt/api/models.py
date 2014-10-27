import datetime
import os
import time

from django.conf import settings
from django.db import models

import commonware.log
from aesfield.field import AESField

from mkt.site.models import ModelBase
from mkt.users.models import UserProfile


REQUEST_TOKEN = 0
ACCESS_TOKEN = 1
TOKEN_TYPES = ((REQUEST_TOKEN, u'Request'), (ACCESS_TOKEN, u'Access'))


log = commonware.log.getLogger('z.api')


class Failure(ModelBase):
    failures = models.IntegerField(default=0)
    locked_out = models.DateTimeField(blank=True, null=True)

    def has_succeeded(self):
        # This will get called a lot, exit quickly.
        if not self.is_locked_out():
            return

        self.failures = 0
        self.locked_out = None
        log.warning('Unlocking user: {0}'.format(self.user.pk))

    def has_failed(self):
        self.failures = models.F('failures') + 1
        if self.failures >= settings.MAX_API_LOGIN_FAILURES:
            self.locked_out = datetime.datetime.now()

        self.save()
        log.warning('Locking user: {0}'.format(self.user.pk))

    def is_locked_out(self):
        return bool(self.locked_out)


class Access(Failure):
    key = models.CharField(max_length=255, unique=True)
    secret = AESField(max_length=255, aes_key='api:access:secret')
    user = models.ForeignKey(UserProfile)
    redirect_uri = models.CharField(max_length=255)
    app_name = models.CharField(max_length=255)

    class Meta:
        db_table = 'api_access'


class Token(Failure):
    token_type = models.SmallIntegerField(choices=TOKEN_TYPES)
    creds = models.ForeignKey(Access)
    key = models.CharField(max_length=255)
    secret = models.CharField(max_length=255)
    timestamp = models.IntegerField()
    user = models.ForeignKey(UserProfile, null=True)
    verifier = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'oauth_token'

    @classmethod
    def generate_new(cls, token_type, creds, user=None):
        return cls.objects.create(
            token_type=token_type,
            creds=creds,
            key=generate(),
            secret=generate(),
            timestamp=time.time(),
            verifier=generate() if token_type == REQUEST_TOKEN else None,
            user=user)


class Nonce(ModelBase):
    nonce = models.CharField(max_length=128)
    timestamp = models.IntegerField()
    client_key = models.CharField(max_length=255)
    request_token = models.CharField(max_length=128, null=True)
    access_token = models.CharField(max_length=128, null=True)

    class Meta:
        db_table = 'oauth_nonce'
        unique_together = ('nonce', 'timestamp', 'client_key',
                           'request_token', 'access_token')


def generate():
    return os.urandom(64).encode('hex')
