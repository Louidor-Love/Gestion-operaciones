from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager


class User(AbstractBaseUser, PermissionsMixin):    
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=765, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    whatsapp_phone = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Telefono WhatsApp (+54)"
    )
    last_name = models.CharField(
        max_length=100,
        null=True,
    )
    first_name = models.CharField(
        max_length=100,
        null=True,
    )
    
    @property
    def full_name(self):
        return u"{} {}".format(self.first_name if self.first_name else '',
                               self.last_name if self.last_name else '')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    objects = UserManager()

    class Meta:
        app_label = 'rapihogar'
        verbose_name = _('RapiHogar User')
        verbose_name_plural = _('RapiHogar Users')  


class Scheme(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = 'rapihogar'
        verbose_name = _('Esquema de un pedido')
        verbose_name_plural = _('Esquemas de pedidos')


#modelo de tecnico que trabaja en los pedidos
class Tecnico(models.Model):
    first_name = models.CharField(
        max_length=100, 
        verbose_name='Nombre'
    )
    last_name = models.CharField(
        max_length=100, 
        verbose_name='Apellido'
    )
    email = models.EmailField(
        unique=True, 
        verbose_name='Email'
    )
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        verbose_name='Teléfono'
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de ingreso'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    #Calcular total de horas trabajadas por el técnico
    def total_hours_worked(self):
        return self.pedidos.aggregate(
            total=models.Sum('hours_worked')
        )['total'] or 0

    #Obtener cantidad total de pedidos
    def total_pedidos(self):
        return self.pedidos.count()
    
    # Calcular pago según la tabla de escalas:
    # 0-14: 200/hora - 15% descuento
    # 15-28: 250/hora - 16% descuento 
    # 29-47: 300/hora - 17% descuento
    # >48: 350/hora - 18% descuento
    def calculate_payment(self):
        total_hours = self.total_hours_worked()
        
        if total_hours <= 14:
            hourly_rate = 200
            discount_rate = 0.15
        elif total_hours <= 28:
            hourly_rate = 250
            discount_rate = 0.16
        elif total_hours <= 47:
            hourly_rate = 300
            discount_rate = 0.17
        else:
            hourly_rate = 350
            discount_rate = 0.18
            
        gross_payment = total_hours * hourly_rate
        discount = gross_payment * discount_rate
        return gross_payment - discount

    def __str__(self):
        return self.full_name

    class Meta:
        app_label = 'rapihogar'
        verbose_name = _('Técnico')
        verbose_name_plural = _('Técnicos')
        ordering = ['-date_joined']

class Company(models.Model):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=80, blank=True, null=True)
    website = models.CharField(max_length=100)

    class Meta:
        app_label = 'rapihogar'
        verbose_name = _('Empresa')
        verbose_name_plural = _('Empresas')


class Pedido(models.Model):
    SOLICITUD = 0
    PEDIDO = 1

    TIPO_PEDIDO = (
        (SOLICITUD, 'Solicitud'),
        (PEDIDO, 'Pedido'),
    )
    type_request = models.IntegerField(
        choices=TIPO_PEDIDO,
        db_index=True,
        default=PEDIDO
    )
    client = models.ForeignKey(
        User,
        verbose_name='cliente',
        on_delete=models.CASCADE
    )
    scheme = models.ForeignKey(
        Scheme,
        null=True,
        on_delete=models.CASCADE
    )
    #tecnico
    tecnico = models.ForeignKey(
        Tecnico,
        related_name='pedidos',
        verbose_name='Técnico asignado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    hours_worked = models.IntegerField(
        default=0,
        verbose_name='Horas trabajadas'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
        verbose_name='Fecha de actualización'
    )

    def __str__(self):
        return f"Pedido #{self.id} - {self.client.full_name}"

    class Meta:
        app_label = 'rapihogar'
        verbose_name_plural = 'pedidos'
        ordering = ('-id', )
