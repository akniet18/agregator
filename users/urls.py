from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'list', UserList, basename='users')

urlpatterns = [
   path('register/', Register.as_view()),
   path('login/', Login.as_view()),
   path('change/password/', changePassword.as_view())
]
urlpatterns += router.urls
