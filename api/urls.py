from rapihogar.models import Company
from rest_framework import routers
from django.urls import path, include
from .views import CompanyViewSet, SecretView

router = routers.DefaultRouter()
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'stats', SecretView, basename='stats')


urlpatterns = [
    path('', include(router.urls)),
]
