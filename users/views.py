from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from .serializers import *
import random
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import User
import uuid
from push_notifications.models import APNSDevice, GCMDevice



class Register(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        s = RegisterSer(data=request.data)
        if s.is_valid():
            username = s.validated_data['username']
            email = s.validated_data['email']
            password = s.validated_data['password']
            if User.objects.filter(username=username).exists():
                return Response({'status': 'username exists'})
            elif User.objects.filter(email=email).exists():
                return Response({'status': 'email exists'})
            else:
                user = User.objects.create(username=username, email=email)
                user.set_password(password)
                user.save()
                return Response({'status': 'ok'})
        else:
            return Response(s.errors)



class Login(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        s = LoginSer(data=request.data)
        if s.is_valid():
            username = s.validated_data['username']
            password = s.validated_data['password']
            user = User.objects.get(username=username)
            success = user.check_password(password)
            if success:
                if Token.objects.filter(user=user).exists():
                    token = Token.objects.get(user=user)
                else:
                    token = Token.objects.create(user=user)
                return Response({'key': token.key, 'uid': user.pk})
            else:
                return Response({'status': 'wrong'})
        else:
            return Response(s.errors)



class UserList(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSer
    queryset = User.objects.filter(is_superuser=False, is_staff=False)



class changePassword(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        s = EmailSer(data=request.data)
        if s.is_valid():
            email = s.validated_data['email']
            pwd = uuid.uuid4().hex[:10]
            user = User.objects.filter(email=email)
            if user.exists():
                user = user[0]
                user.set_password(pwd)
                user.save()
                send_mail(
                    'Agregator password', 
                    f'Your password: {pwd}', 
                    settings.EMAIL_HOST_USER,
                    [email,], 
                    fail_silently=False)
                return Response({'status':'ok'})
            else:
                return Response({'status': 'not found'})
        else:
            return Response(s.errors)

            
class pushRegister(APIView):
    permission_classes = [permissions.IsAuthenticated,]
    
    def post(self, request):
        s = pushSerializer(data=request.data)
        if s.is_valid():
            android = GCMDevice.objects.filter(user=request.user)
            if android.exists():
                android = GCMDevice.objects.get(user=request.user)
                android.registration_id = s.validated_data['reg_id']
                android.save()
            else:
                GCMDevice.objects.create(user=request.user, active=True,
                                    registration_id=s.validated_data['reg_id'],
                                    cloud_message_type="FCM")
            return Response({'status': "ok"})
        else:
            return Response(s.errors)


class supportApi(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        s = supportSer(data=request.data)
        if s.is_valid():
            text = s.validated_data['text']
            send_mail(
                    'Agregator', 
                    f'{text}', 
                    settings.EMAIL_HOST_USER,
                    [settings.EMAIL_HOST_USER,], 
                    fail_silently=False)
            return Response({'status': 'ok'})
        else:
            return Response(s.errors)