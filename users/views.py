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



