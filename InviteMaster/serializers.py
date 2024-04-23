from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    referrals = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'invite_code', 'referral_code', 'used_count', 'active', 'referrals']


    def get_referrals(self, obj):
        return UserProfile.objects.filter(referral_code=obj.invite_code).values_list('phone_number', flat=True)


class AuthorizationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=10)
    authorization_code = serializers.CharField(max_length=4)


class ReferralCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=10)
    referral_code = serializers.CharField(max_length=6)


class GenerateCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=10)


