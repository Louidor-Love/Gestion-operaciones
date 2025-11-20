"""
Comando para crear técnicos de prueba
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from rapihogar.models import Tecnico


class Command(BaseCommand):
    help = 'Crea 5 técnicos de prueba para el sistema'

    def handle(self, *args, **options):
        tecnicos_data = [
            {
                'first_name': 'Bastien',
                'last_name': 'Pérez',
                'email': 'bastien.perez@rapihogar.com',
                'phone': '+54911123456'
            },
            {
                'first_name': 'Luisa',
                'last_name': 'González',
                'email': 'luisa.gonzalez@rapihogar.com',
                'phone': '+54911234567'
            },
            {
                'first_name': 'Roberto',
                'last_name': 'Martínez',
                'email': 'roberto.martinez@rapihogar.com',
                'phone': '+54911345678'
            },
            {
                'first_name': 'Ana Sofía',
                'last_name': 'Rodríguez',
                'email': 'ana.rodriguez@rapihogar.com',
                'phone': '+54911456789'
            },
            {
                'first_name': 'Diego',
                'last_name': 'Fernández',
                'email': 'diego.fernandez@rapihogar.com',
                'phone': '+54911567890'
            }
        ]
        
        tecnicos_creados = 0
        
        try:
            with transaction.atomic():
                for data in tecnicos_data:
                    tecnico, created = Tecnico.objects.get_or_create(
                        email=data['email'],
                        defaults=data
                    )
                    
                    if created:
                        tecnicos_creados += 1
                        self.stdout.write(
                            f'✅ Técnico creado: {tecnico.full_name}'
                        )
                    else:
                        self.stdout.write(
                            f'⚠️  Ya existe: {tecnico.full_name}'
                        )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🎉 Proceso completado. '
                    f'Técnicos nuevos creados: {tecnicos_creados}/5'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Error al crear técnicos: {str(e)}'
                )
            )