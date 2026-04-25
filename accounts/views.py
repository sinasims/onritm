# accounts/views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework import serializers
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer, ChangePasswordSerializer, VerifyOTPSerializer, RequestOTPSerializer
)
from .models import User, OTPCode  # اگر مدل سفارشی را در accounts دارید
from .utils import send_sms_via_smsir


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            return Response({'error': 'نام کاربری یا رمز عبور اشتباه است.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': 'رمز فعلی صحیح نیست.'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'رمز عبور با موفقیت تغییر کرد.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # نیاز به تنظیم 'rest_framework_simplejwt.token_blacklist' در INSTALLED_APPS
            return Response({'message': 'خروج موفقیت‌آمیز بود.'})
        except Exception:
            return Response({'error': 'توکن نامعتبر است.'}, status=status.HTTP_400_BAD_REQUEST)
        

class RequestOTPView(APIView):
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone_number']
        otp = OTPCode.generate_code(phone)
        sent = send_sms_via_smsir(phone, otp.code)
        print(sent)
        if sent:
            return Response({'message': 'کد تأیید ارسال شد.'})
        else:
            return Response({'error': 'ارسال پیامک ناموفق بود. لطفاً بعداً تلاش کنید.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class VerifyOTPLoginView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone_number']
        code = serializer.validated_data['code']
        
        try:
            otp = OTPCode.objects.get(phone_number=phone, code=code)
        except OTPCode.DoesNotExist:
            return Response({'error': 'کد نامعتبر است.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not otp.is_valid():
            otp.delete()
            return Response({'error': 'کد منقضی شده است.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # پیدا کردن یا ساخت کاربر
        user, created = User.objects.get_or_create(
            phone_number=phone,
            defaults={'username': phone}  # در صورت نیاز username را با شماره تلفن پر کن
        )
        # اگر کاربر بدون username ساخته شده، می‌توانیم username را تصحیح کنیم
        if created and not user.username:
            user.username = f'user_{phone[-4:]}'
            user.save()
        
        # پاک کردن OTP پس از استفاده
        otp.delete()
        
        # تولید توکن JWT
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)
        return Response({
            'user': user_serializer.data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'is_new': created,
        })
    
