from rest_framework import serializers
from .models import User


class RegisterSer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField()


class LoginSer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class EmailSer(serializers.Serializer):
    email = serializers.CharField()
    

class UserSer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'address')
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance
