from django.db import models

import uuid, random, string


class UserProfile(models.Model):
    phone_number = models.CharField(max_length=10, unique=True)
    invite_code = models.CharField(max_length=6, unique=True)
    referral_code = models.CharField(max_length=6, blank=True)
    authorization_code = models.CharField(max_length=4)
    used_count = models.IntegerField(default=0)
    active = models.BooleanField(default=False)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)


    @staticmethod
    def generate_referral_code():
        return uuid.uuid4().hex[:6]

    @staticmethod
    def generate_authorization_code():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=4))

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = self.generate_referral_code()
        if not self.authorization_code or not self.active:
            self.authorization_code = self.generate_authorization_code()
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.phone_number



