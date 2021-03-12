from rest_framework import serializers
from .models import *

class MessageSer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"