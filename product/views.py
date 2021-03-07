from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import generics, permissions, status, views, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from .serializers import *
import random
from django.core.mail import send_mail
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from users.models import User
from categories.models import Category


class getProduct(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny,]
    queryset = Product.objects.all()
    serializer_class = ProductSer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ('name', 'description')
    filter_fields = ('category', )
    

class createProduct(APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        s = CreateProductSer(data=request.data)
        if s.is_valid():
            p = Product.objects.create(
                name = s.validated_data['name'],
                manufacturer = Manufacture.objects.get(id=s.validated_data['manufacturer']),
                description = s.validated_data['description'],
                composition = s.validated_data['composition'],
                category = Category.objects.get(id = s.validated_data['category']),
                photo = s.validated_data['photo']
            )
            c = CountProduct.objects.create(
                product = p,
                pharmacy = request.user.my_pharmacy.all()[0],
                price = s.validated_data['price'],
                count = s.validated_data['count']
            )
            return Response({'status': 'ok'})
        else:
            return Response(s.errors)



class PharmacyApi(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        s = PharmacySer(data=request.data)
        if s.is_valid():
            p = Pharmacy.objects.create(
                name = s.validated_data['name'],
                owner = request.user,
                address = s.validated_data['address'],
                working_hours = s.validated_data['working_hours'],
                city = s.validated_data['city'],
                phone = s.validated_data['phone']
            )
            return Response({'status': 'ok'})
        else:
             return Response(s.errors)
    
