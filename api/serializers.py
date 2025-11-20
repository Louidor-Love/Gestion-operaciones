"""
Serializers para la API de RapiHogar vaitty
"""
from rest_framework import serializers
from rapihogar.models import Tecnico, Pedido


class TecnicoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Técnico"""
    full_name = serializers.CharField(read_only=True)
    total_hours_worked = serializers.SerializerMethodField()
    total_pedidos = serializers.SerializerMethodField()
    total_payment = serializers.SerializerMethodField()
    
    class Meta:
        model = Tecnico
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 
            'email', 'phone', 'is_active', 'date_joined',
            'total_hours_worked', 'total_pedidos', 'total_payment'
        ]
        read_only_fields = ['date_joined']
    
    def get_total_hours_worked(self, obj):
        return obj.total_hours_worked()
    
    def get_total_pedidos(self, obj):
        return obj.total_pedidos()
    
    def get_total_payment(self, obj):
        return round(obj.calculate_payment(), 2)


class TecnicoListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de técnicos"""
    full_name = serializers.CharField(read_only=True)
    total_hours_worked = serializers.SerializerMethodField()
    total_pedidos = serializers.SerializerMethodField()
    total_payment = serializers.SerializerMethodField()
    
    class Meta:
        model = Tecnico
        fields = [
            'id', 'full_name', 'total_hours_worked', 
            'total_pedidos', 'total_payment'
        ]
    
    def get_total_hours_worked(self, obj):
        return obj.total_hours_worked()
    
    def get_total_pedidos(self, obj):
        return obj.total_pedidos()
    
    def get_total_payment(self, obj):
        return round(obj.calculate_payment(), 2)


class InformeSerializer(serializers.Serializer):
    """Serializer para el informe de técnicos"""
    monto_promedio = serializers.DecimalField(max_digits=10, decimal_places=2)
    tecnicos_bajo_promedio = TecnicoListSerializer(many=True)
    ultimo_trabajador_monto_bajo = TecnicoListSerializer()
    ultimo_trabajador_monto_alto = TecnicoListSerializer()
    
    # Estadísticas adicionales
    total_tecnicos = serializers.IntegerField()
    total_horas_sistema = serializers.IntegerField()
    total_pedidos_sistema = serializers.IntegerField()


class PedidoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Pedido (para updates opcionales)"""
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    tecnico_name = serializers.CharField(source='tecnico.full_name', read_only=True)
    scheme_name = serializers.CharField(source='scheme.name', read_only=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'type_request', 'client', 'client_name',
            'tecnico', 'tecnico_name', 'scheme', 'scheme_name',
            'hours_worked', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_hours_worked(self, value):
        """Validar que las horas trabajadas sean positivas"""
        if value < 0:
            raise serializers.ValidationError(
                "Las horas trabajadas no pueden ser negativas."
            )
        return value