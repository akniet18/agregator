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


class ManufSer(serializers.Serializer):
    name = serializers.CharField()


class ProductSer(serializers.ModelSerializer):
    available = CountProductSer(many=True)
    manufacturer = ManufSer()
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


class ProductSer2(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField('get_avatar_url', read_only=True)
    class Meta:
        model = Product
        fields = "__all__"
    def get_avatar_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.photo.url)

class CountProductSer2(serializers.ModelSerializer):
    product = ProductSer2()
    class Meta:
        model = CountProduct
        fields = "__all__"


class Author(serializers.Serializer):
    username = serializers.CharField()


class ReviewSer(serializers.ModelSerializer):
    author = Author()
    class Meta:
        model = Review
        fields = "__all__"

class CreateReviewSer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ('author',)