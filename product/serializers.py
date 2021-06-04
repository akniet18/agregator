from rest_framework import serializers
from .models import *


class PharmacySer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = "__all__"
        read_only_fields = ("owner",)


class PharmacySerCreate(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = "__all__"


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
    photo = serializers.SerializerMethodField('get_avatar_url', read_only=True)
    class Meta:
        model = Product
        fields = "__all__"

    def get_avatar_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.photo.url)


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

class categorySer(serializers.Serializer):
    name = serializers.CharField()
    id = serializers.IntegerField()
class ProductSer3(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField('get_avatar_url', read_only=True)
    category = categorySer()
    class Meta:
        model = Product
        fields = "__all__"
    def get_avatar_url(self, obj):
        return self.context['request'].build_absolute_uri(obj.photo.url)
class CountProductSer3(serializers.ModelSerializer):
    product = ProductSer3()
    pharmacy = PharmacySer()
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


class ReviewProductSer(serializers.ModelSerializer):
    author = Author()
    class Meta:
        model = ReviewProduct
        fields = "__all__"

class CreateReviewProductSer(serializers.ModelSerializer):
    class Meta:
        model = ReviewProduct
        fields = "__all__"
        read_only_fields = ('author',)


class productIdSer(serializers.Serializer):
    id = serializers.IntegerField()