from django.shortcuts import render, redirect
from django.contrib.auth import logout
from rest_framework import generics, status
from rest_framework.response import Response
from .forms import *
from .serializers import *

import random
import time


def home(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            referral_code = form.cleaned_data.get('referral_code', '')
            try:
                user = UserProfile.objects.get(phone_number=phone_number)
            except UserProfile.DoesNotExist:
                user = UserProfile.objects.create(phone_number=phone_number)
                user.referral_code = referral_code
                user.save()
            time.sleep(random.uniform(1, 4))
            user.authorization_code = UserProfile.generate_authorization_code()
            user.save()
            request.session['phone_number'] = phone_number
            return redirect('verify_phone')
    else:
        form = RegistrationForm()
    return render(request, 'InviteMaster/home.html', {'form': form})


def verify_phone(request):
    if 'phone_number' not in request.session:
        return redirect('home')
    phone_number = request.session['phone_number']
    user = UserProfile.objects.get(phone_number=phone_number)
    if request.method == 'POST':
        form = AuthorizationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['authorization_code']
            if code == user.authorization_code:
                print('Authorization successful!')
                user.active = True
                user.save()
                return redirect('profile')
            else:
                print('Invalid authorization code!')
                return redirect('verify_phone')
    else:
        form = AuthorizationForm()
    return render(request, 'InviteMaster/verify_phone.html', {'phone_number': phone_number, 'form': form})


def profile(request):
    if 'phone_number' not in request.session:
        return redirect('home')
    phone_number = request.session['phone_number']
    user = UserProfile.objects.get(phone_number=phone_number)

    if request.method == 'POST':
        form = ReferralCodeForm(request.POST)
        if user.referral_code:
            form = None
            print(user.referral_code)
        if form and form.is_valid():
            code = form.cleaned_data['referral_code']
            try:
                referred_user = UserProfile.objects.get(invite_code=code)
                if not referred_user == user and referred_user.active:
                    referred_user.used_count += 1
                    referred_user.save()
                    user.referral_code = code
                    user.save()
                return redirect('profile')

            except UserProfile.DoesNotExist:
                pass
    else:
        form = ReferralCodeForm() if not user.referral_code else None
    return render(request, 'InviteMaster/profile.html', {'user': user, 'form': form} or redirect('profile'))


def user_logout(request):
    logout(request)
    return redirect('home')


def get_user_by_phone(phone_number):
    try:
        return UserProfile.objects.get(phone_number=phone_number)
    except UserProfile.DoesNotExist:
        return UserProfile.objects.create(phone_number=phone_number)


class GenerateAuthorizationCode(generics.GenericAPIView):
    serializer_class = GenerateCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        user = get_user_by_phone(phone_number)
        user.authorization_code = UserProfile.generate_authorization_code()
        user.save()
        time.sleep(random.uniform(1, 4))
        return Response({"status": "success", "message": f"Authorization code is {user.authorization_code}"}, status=status.HTTP_200_OK)


class UserAuthorization(generics.GenericAPIView):
    serializer_class = AuthorizationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        authorization_code = serializer.validated_data['authorization_code']
        user = get_user_by_phone(phone_number)
        if user.authorization_code == authorization_code:
            user.active = True
            user.save()
            user_serializer = UserProfileSerializer(user)
            return Response({"status": "success", "user": user_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "failure", "message": "Invalid authorization code"}, status=status.HTTP_400_BAD_REQUEST)


class UserReferralCode(generics.GenericAPIView):
    serializer_class = ReferralCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        referral_code = serializer.validated_data['referral_code']
        try:
            current_user = UserProfile.objects.get(phone_number=phone_number)
        except UserProfile.DoesNotExist:
            return Response({"status": "failure", "message": "Invalid phone number"}, status=status.HTTP_400_BAD_REQUEST)
        if current_user.referral_code:
            return Response({"status": "failure", "message": "User has already activated a referral code"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            referred_user = UserProfile.objects.get(invite_code=referral_code)
        except UserProfile.DoesNotExist:
            return Response({"status": "failure", "message": "Invalid invite code"}, status=status.HTTP_400_BAD_REQUEST)
        if not referred_user.active:
            return Response({"status": "failure", "message": "Referred user is not active"}, status=status.HTTP_400_BAD_REQUEST)
        if referred_user == current_user:
            return Response({"status": "failure", "message": "User cannot activate their own invite code"}, status=status.HTTP_400_BAD_REQUEST)
        referred_user.used_count += 1
        referred_user.save()
        current_user.referred_by = referred_user
        current_user.referral_code = referral_code
        current_user.save()
        return Response({"status": "success"}, status=status.HTTP_200_OK)