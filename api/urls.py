from rapihogar.models import Company
from rest_framework import routers
from django.urls import path, include
from . import views

router = routers.DefaultRouter()
router.register(r'company', views.CompanyViewSet, basename='company')
router.register(r'stats', views.SecretView, basename='stats')


urlpatterns = [
    path('', include(router.urls)),
    path('tecnicos/', views.TecnicoListAPIView.as_view(), name='tecnicos-list'),
    path('informe/', views.informe_tecnicos_view, name='informe-tecnicos'),

    # API opcional para actualizar pedidos
    path('pedidos/<int:pk>/', views.PedidoUpdateAPIView.as_view(), name='pedido-update'),

]
