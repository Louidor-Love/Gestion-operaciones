"""
Comando para generar pedidos aleatorios
"""
import random
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from rapihogar.models import Tecnico, User, Scheme, Pedido


class Command(BaseCommand):
    help = 'Genera N pedidos aleatorios (entre 1 y 100)'

    def add_arguments(self, parser):
        parser.add_argument(
            'cantidad',
            type=int,
            help='Número de pedidos a generar (1-100)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar información detallada del proceso'
        )

    def handle(self, *args, **options):
        cantidad = options['cantidad']
        verbose = options['verbose']
        
        # Validar rango
        if cantidad < 1 or cantidad > 100:
            raise CommandError(
                'La cantidad debe estar entre 1 y 100 (inclusive). '
                f'Recibido: {cantidad}'
            )
        
        # Verificar que existan los datos necesarios
        tecnicos = list(Tecnico.objects.filter(is_active=True))
        clientes = list(User.objects.filter(is_active=True))
        esquemas = list(Scheme.objects.all())
        
        if not tecnicos:
            raise CommandError(
                'No hay técnicos activos en el sistema. '
                'Ejecuta: python manage.py crear_tecnicos'
            )
        
        if not clientes:
            raise CommandError(
                'No hay usuarios/clientes en el sistema. '
                'Carga los fixtures primero.'
            )
        
        if not esquemas:
            raise CommandError(
                'No hay esquemas en el sistema. '
                'Carga los fixtures primero.'
            )
        
        if verbose:
            self.stdout.write(f'📊 Datos disponibles:')
            self.stdout.write(f'   • Técnicos activos: {len(tecnicos)}')
            self.stdout.write(f'   • Clientes: {len(clientes)}')
            self.stdout.write(f'   • Esquemas: {len(esquemas)}')
            self.stdout.write('')
        
        pedidos_creados = []
        
        try:
            with transaction.atomic():
                for i in range(cantidad):
                    # Seleccionar datos aleatorios
                    tecnico = random.choice(tecnicos)
                    cliente = random.choice(clientes)
                    esquema = random.choice(esquemas)
                    horas = random.randint(1, 10)
                    
                    # Crear pedido
                    pedido = Pedido.objects.create(
                        client=cliente,
                        tecnico=tecnico,
                        scheme=esquema,
                        hours_worked=horas,
                        type_request=Pedido.PEDIDO
                    )
                    
                    pedidos_creados.append(pedido)
                    
                    if verbose:
                        self.stdout.write(
                            f'✅ Pedido #{pedido.id}: '
                            f'{tecnico.full_name} → {cliente.full_name} '
                            f'({horas}h)'
                        )
            
            # Resumen final
            total_horas = sum(p.hours_worked for p in pedidos_creados)
            
            self.stdout.write('')
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 ¡Proceso completado exitosamente!'
                )
            )
            self.stdout.write(f'   • Pedidos creados: {len(pedidos_creados)}')
            self.stdout.write(f'   • Total horas asignadas: {total_horas}')
            self.stdout.write('')
            self.stdout.write(
                '💡 Puedes ver los pedidos en el admin: /admin/rapihogar/pedido/'
            )
            
        except Exception as e:
            raise CommandError(f'Error al crear pedidos: {str(e)}')