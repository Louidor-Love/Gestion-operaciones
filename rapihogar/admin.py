""" Register models """

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Company, Scheme, Pedido, Tecnico


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configurado para el modelo User personalizado"""
    list_display = ('email', 'full_name', 'username', 'is_staff', 'is_active', 'whatsapp_phone')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'username', 'whatsapp_phone')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas Importantes', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Admin para el modelo Company"""
    list_display = ('name', 'email', 'phone', 'website')
    search_fields = ('name', 'email')
    list_filter = ('name',)


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    """Admin para el modelo Scheme"""
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Tecnico)
class TecnicoAdmin(admin.ModelAdmin):
    """Admin para el modelo Tecnico"""
    list_display = ('full_name', 'email', 'phone', 'is_active', 'date_joined', 'total_pedidos_display', 'total_hours_display', 'total_payment_display')
    list_filter = ('is_active', 'date_joined')
    search_fields = ('first_name', 'last_name', 'email')
    readonly_fields = ('date_joined', 'total_pedidos_display', 'total_hours_display', 'total_payment_display')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Estado', {
            'fields': ('is_active', 'date_joined')
        }),
        ('Estadísticas', {
            'fields': ('total_pedidos_display', 'total_hours_display', 'total_payment_display'),
            'classes': ('collapse',)
        }),
    )
    
    def total_pedidos_display(self, obj):
        return obj.total_pedidos()
    total_pedidos_display.short_description = 'Total Pedidos'
    
    def total_hours_display(self, obj):
        return f"{obj.total_hours_worked()} hrs"
    total_hours_display.short_description = 'Horas Trabajadas'
    
    def total_payment_display(self, obj):
        return f"${obj.calculate_payment():,.2f}"
    total_payment_display.short_description = 'Pago Total'


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """Admin para el modelo Pedido"""
    list_display = ('id', 'client', 'tecnico', 'get_type_display', 'hours_worked', 'scheme', 'created_at')
    list_filter = ('type_request', 'created_at', 'tecnico', 'scheme')
    search_fields = ('client__email', 'client__first_name', 'client__last_name', 'tecnico__first_name', 'tecnico__last_name')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('type_request', 'client', 'tecnico', 'scheme')
        }),
        ('Trabajo', {
            'fields': ('hours_worked',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_type_display(self, obj):
        return obj.get_type_request_display()
    get_type_display.short_description = 'Tipo'
