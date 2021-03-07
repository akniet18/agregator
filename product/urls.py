from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register(r'list', UserList, basename='users')

urlpatterns = [
   path('', getProduct.as_view({'get': 'list'})),
   path('create/', createProduct.as_view()),
   path('pharmacy/create/', PharmacyApi.as_view())
]
# urlpatterns += router.urls
