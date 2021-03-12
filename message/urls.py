from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'', MessageApi, basename='users')

urlpatterns = [
   
]
urlpatterns += router.urls
