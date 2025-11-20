from rest_framework import viewsets, permissions, serializers, generics, status, filters
from rapihogar.models import Company, Pedido, Tecnico
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
import logging
from django.conf import settings
from django.db.models import Q, Sum, Avg
from decimal import Decimal
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import ( TecnicoSerializer,   TecnicoListSerializer, InformeSerializer,PedidoSerializer)

logger = logging.getLogger(__name__)

class CompanySerializer(serializers.ModelSerializer):
  
    class Meta:
        model = Company
        fields = '__all__'

class LegacyPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
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
        
# NUEVAS VISTAS
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TecnicoListAPIView(generics.ListAPIView):
    """
    API para listar técnicos con información de pagos y filtros
    
    Funcionalidades:
    - Lista todos los técnicos activos
    - Calcula automáticamente horas trabajadas, cantidad de pedidos y pago total
    - Filtro por nombre (búsqueda parcial)
    - Ordenamiento por diferentes campos
    - Paginación
    """
    queryset = Tecnico.objects.filter(is_active=True).prefetch_related('pedidos')
    serializer_class = TecnicoListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtro por nombre (búsqueda parcial)
    search_fields = ['first_name', 'last_name']
    
    # Campos por los que se puede ordenar
    ordering_fields = ['date_joined', 'first_name', 'last_name']
    ordering = ['-date_joined']  # Orden por defecto
    
    def get_queryset(self):
        queryset_first = super().get_queryset()        
        queryset = queryset_first.prefetch_related('pedidos')
        
        # Log de consulta
        logger.info(f'API Técnicos: Consulta ejecutada con {queryset.count()} resultados')
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            
            total_count = self.get_queryset().count()
            response.data['meta'] = {
                'total_tecnicos': total_count,
                'filtros_aplicados': {
                    'search': request.query_params.get('search', None),
                    'ordering': request.query_params.get('ordering', '-date_joined')
                }
            }
            
            logger.info(f'API Técnicos: Respuesta exitosa con {len(response.data["results"])} elementos')
            return response
            
        except Exception as e:
            logger.error(f'Error en API Técnicos: {str(e)}')
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
def informe_tecnicos_view(request):
    """
    API para obtener informe detallado de técnicos
    
    Retorna:
    - Monto promedio cobrado por todos los técnicos
    - Datos de técnicos que cobraron menos que el promedio
    - El último trabajador ingresado que cobró el monto más bajo
    - El último trabajador ingresado que cobró el monto más alto
    """
    try:
        # Obtener todos los técnicos activos con sus datos calculados
        tecnicos = Tecnico.objects.filter(is_active=True).prefetch_related('pedidos')
        
        if not tecnicos.exists():
            return Response(
                {'error': 'No hay técnicos activos en el sistema'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calcular datos para cada técnico
        tecnicos_data = []
        for tecnico in tecnicos:
            tecnico_info = {
                'tecnico': tecnico,
                'pago': tecnico.calculate_payment(),
                'horas': tecnico.total_hours_worked(),
                'pedidos': tecnico.total_pedidos()
            }
            tecnicos_data.append(tecnico_info)
        
        # Calcular monto promedio
        pagos = [data['pago'] for data in tecnicos_data if data['pago'] > 0]
        monto_promedio = sum(pagos) / len(pagos) if pagos else 0
        
        # Técnicos que cobraron menos que el promedio
        tecnicos_bajo_promedio = [
            data['tecnico'] for data in tecnicos_data 
            if data['pago'] < monto_promedio
        ]
        
        # Último trabajador (por fecha de ingreso) con monto más bajo
        tecnico_monto_bajo = min(
            tecnicos_data, 
            key=lambda x: (x['pago'], -x['tecnico'].date_joined.timestamp())
        )['tecnico']
        
        # Último trabajador (por fecha de ingreso) con monto más alto
        tecnico_monto_alto = max(
            tecnicos_data, 
            key=lambda x: (x['pago'], -x['tecnico'].date_joined.timestamp())
        )['tecnico']
        
        # Estadísticas adicionales del sistema
        total_horas_sistema = sum(data['horas'] for data in tecnicos_data)
        total_pedidos_sistema = sum(data['pedidos'] for data in tecnicos_data)
        
        # Preparar datos para el serializer
        informe_data = {
            'monto_promedio': Decimal(str(round(monto_promedio, 2))),
            'tecnicos_bajo_promedio': tecnicos_bajo_promedio,
            'ultimo_trabajador_monto_bajo': tecnico_monto_bajo,
            'ultimo_trabajador_monto_alto': tecnico_monto_alto,
            'total_tecnicos': len(tecnicos_data),
            'total_horas_sistema': total_horas_sistema,
            'total_pedidos_sistema': total_pedidos_sistema
        }
        
        # Serializar y retornar
        serializer = InformeSerializer(informe_data)
        
        logger.info(f'API Informe: Generado exitosamente para {len(tecnicos_data)} técnicos')
        
        return Response({
            'informe': serializer.data,
            'meta': {
                'fecha_generacion': 'now',
                'criterio_ultimo_trabajador': 'Fecha de ingreso más reciente'
            }
        })
        
    except Exception as e:
        logger.error(f'Error en API Informe: {str(e)}')
        return Response(
            {'error': 'Error al generar el informe'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class PedidoUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    API para actualizar pedidos (endpoint opcional)
    
    Permite:
    - Obtener detalles de un pedido específico
    - Actualizar campos del pedido (solo algunos campos editables)
    """
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer
    
    def get_queryset(self):
        """Optimizar consulta con select_related"""
        return super().get_queryset().select_related('client', 'tecnico', 'scheme')
    
    def update(self, request, *args, **kwargs):
        """Override para agregar logging y validaciones adicionales"""
        try:
            instance = self.get_object()
            old_hours = instance.hours_worked
            
            response = super().update(request, *args, **kwargs)
            
            # Log del cambio
            new_hours = instance.hours_worked
            logger.info(
                f'Pedido #{instance.id} actualizado: '
                f'Horas {old_hours} -> {new_hours} por usuario API'
            )
            
            return response
            
        except Exception as e:
            logger.error(f'Error al actualizar pedido: {str(e)}')
            return Response(
                {'error': 'Error al actualizar el pedido'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )