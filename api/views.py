from rest_framework import viewsets, permissions, serializers
from rapihogar.models import Company, Pedido
from rest_framework.response import Response
from rest_framework import status
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class CompanySerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Company
        fields = '__all__'


class PedidoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Pedido
        fields = '__all__'

class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            companies = self.get_queryset()
            data = []
            for company in companies:
                email_lower = company.email.lower()
                data.append({
                    "id": company.id,
                    "name": company.name,
                    "email": email_lower
                })

            return Response(data)
        except Exception as e:
            logger.error("Error procesando CompanyViewSet.list", exc_info=True)
            return Response({"error": "Ocurrió un error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SecretView(viewsets.ModelViewSet):
    serializer_class = PedidoSerializer
    queryset = Pedido.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            pedidos = Pedido.objects.filter(client__pk=settings.SECRET_CLIENT_ID)
            return Response(pedidos)
        except Exception as e:
            logger.error("Error procesando SecretView.list", exc_info=True)
            return Response({"error": "Ocurrió un error inesperado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)