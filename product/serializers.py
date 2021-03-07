from rest_framework import serializers
from .models import *


class PharmacySer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = "__all__"
        read_only_fields = ("owner",)


class CountProductSer(serializers.ModelSerializer):
    pharmacy = PharmacySer()
    class Meta:
        model = CountProduct
        fields = "__all__"


class ProductSer(serializers.ModelSerializer):
    available = CountProductSer(many=True)
    class Meta:
        model = Product
        fields = "__all__"


class CreateProductSer(serializers.Serializer):
    name = serializers.CharField()
    manufacturer = serializers.IntegerField()
    description = serializers.CharField()
    composition = serializers.CharField()
    price = serializers.IntegerField()
    count = serializers.IntegerField()
    photo = serializers.FileField()
    category = serializers.IntegerField()


