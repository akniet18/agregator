from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register(r'list', UserList, basename='users')

urlpatterns = [
   path('', getProduct.as_view({'get': 'list'})),
   path('create/', createProduct.as_view()),
   path('pharmacy/create/', PharmacyApi.as_view()),
   path('accounting/', Accounting.as_view()),
   path('review/<id>', ReviewApi.as_view()),
   path('create/review/', CreateReview.as_view()),

   path('review/p/<id>', ReviewProductApi.as_view()),
   path('create/review/p/', CreateProductReview.as_view()),

   path('recomendation/', Recomendation.as_view()),
   path('pharmacy/', PharmacyS.as_view({'get': 'list'})),

   path("favorites", favorites.as_view()),
]
# urlpatterns += router.urls
