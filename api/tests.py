import json
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rapihogar.models import Tecnico, Pedido, Scheme, Company
from django.urls import reverse

from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()

class CompanyListCreateAPIViewTestCase(APITestCase):
    url = reverse("company-list")

    def setUp(self):
        self.username = "user_test"
        self.email = "test@rapihigar.com"
        self.password = "Rapi123"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_create_company(self):
        response = self.client.post(self.url,
                                    {
                                        "name": "company delete!",
                                        "phone": "123456789",
                                        "email": "test@rapihigar.com",
                                        "website": "http://www.rapitest.com"
                                    }
                                    )
        self.assertEqual(201, response.status_code)

    def test_list_company(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertTrue(len(json.loads(response.content)) == Company.objects.count())


# Los test
class TecnicoModelTest(TestCase):
    """Tests para el modelo Técnico"""
    
    def setUp(self):
        self.tecnico = Tecnico.objects.create(
            first_name='Juan',
            last_name='Pérez',
            email='juan.perez@test.com',
            phone='+54911123456'
        )
        
        self.cliente = User.objects.create_user(
            email='cliente@test.com',
            first_name='Cliente',
            last_name='Test',
            username='cliente_test'
        )
        
        self.scheme = Scheme.objects.create(name='Esquema Test')
    
    def test_tecnico_full_name(self):
        """Test del property full_name"""
        self.assertEqual(self.tecnico.full_name, 'Juan Pérez')
    
    def test_tecnico_str(self):
        """Test del método __str__"""
        self.assertEqual(str(self.tecnico), 'Juan Pérez')
    
    def test_total_hours_worked_sin_pedidos(self):
        """Test de total_hours_worked sin pedidos"""
        self.assertEqual(self.tecnico.total_hours_worked(), 0)
    
    def test_total_pedidos_sin_pedidos(self):
        """Test de total_pedidos sin pedidos"""
        self.assertEqual(self.tecnico.total_pedidos(), 0)
    
    def test_calculate_payment_sin_pedidos(self):
        """Test de calculate_payment sin pedidos"""
        self.assertEqual(self.tecnico.calculate_payment(), 0)
    
    def test_calculate_payment_0_14_horas(self):
        """Test de calculate_payment para 0-14 horas"""
        # Crear pedido con 10 horas
        Pedido.objects.create(
            client=self.cliente,
            tecnico=self.tecnico,
            scheme=self.scheme,
            hours_worked=10
        )
        
        # 10 horas * 200/hora = 2000
        # Descuento 15%: 2000 * 0.15 = 300
        # Total: 2000 - 300 = 1700
        expected_payment = 1700
        self.assertEqual(self.tecnico.calculate_payment(), expected_payment)
    
    def test_calculate_payment_15_28_horas(self):
        """Test de calculate_payment para 15-28 horas"""
        # Crear pedidos que sumen 20 horas
        Pedido.objects.create(
            client=self.cliente,
            tecnico=self.tecnico,
            scheme=self.scheme,
            hours_worked=15
        )
        Pedido.objects.create(
            client=self.cliente,
            tecnico=self.tecnico,
            scheme=self.scheme,
            hours_worked=5
        )
        
        # 20 horas * 250/hora = 5000
        # Descuento 16%: 5000 * 0.16 = 800
        # Total: 5000 - 800 = 4200
        expected_payment = 4200
        self.assertEqual(self.tecnico.calculate_payment(), expected_payment)


class TecnicoAPITest(APITestCase):
    """Tests para la API de técnicos"""
    
    def setUp(self):
        # Crear técnicos de prueba
        self.tecnico1 = Tecnico.objects.create(
            first_name='Juan',
            last_name='Pérez',
            email='juan.perez@test.com'
        )
        
        self.tecnico2 = Tecnico.objects.create(
            first_name='María',
            last_name='González',
            email='maria.gonzalez@test.com'
        )
        
        # Crear cliente y esquema
        self.cliente = User.objects.create_user(
            email='cliente@test.com',
            first_name='Cliente',
            last_name='Test',
            username='cliente_test'
        )
        
        self.scheme = Scheme.objects.create(name='Esquema Test')
        
        # Crear algunos pedidos
        Pedido.objects.create(
            client=self.cliente,
            tecnico=self.tecnico1,
            scheme=self.scheme,
            hours_worked=10
        )
        
        Pedido.objects.create(
            client=self.cliente,
            tecnico=self.tecnico2,
            scheme=self.scheme,
            hours_worked=25
        )
    
    def test_tecnicos_list_api(self):
        """Test del endpoint de listado de técnicos"""
        url = reverse('tecnicos-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('meta', response.data)
        self.assertEqual(len(response.data['results']), 2)
        
        # Verificar estructura de datos
        tecnico_data = response.data['results'][0]
        required_fields = ['id', 'full_name', 'total_hours_worked', 'total_pedidos', 'total_payment']
        for field in required_fields:
            self.assertIn(field, tecnico_data)
    
    def test_tecnicos_search_filter(self):
        """Test del filtro de búsqueda por nombre"""
        url = reverse('tecnicos-list')
        response = self.client.get(url, {'search': 'Juan'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['full_name'], 'Juan Pérez')


class InformeAPITest(APITestCase):
    """Tests para la API de informe"""
    
    def setUp(self):
        # Crear técnicos con diferentes pagos
        self.tecnico1 = Tecnico.objects.create(
            first_name='Juan',
            last_name='Pérez',
            email='juan.perez@test.com'
        )
        
        self.tecnico2 = Tecnico.objects.create(
            first_name='María',
            last_name='González',
            email='maria.gonzalez@test.com'
        )
        
        # Crear cliente y esquema
        self.cliente = User.objects.create_user(
            email='cliente@test.com',
            first_name='Cliente',
            last_name='Test',
            username='cliente_test'
        )
        
        self.scheme = Scheme.objects.create(name='Esquema Test')
        
        # Crear pedidos con diferentes horas
        Pedido.objects.create(
            client=self.cliente,
            tecnico=self.tecnico1,
            scheme=self.scheme,
            hours_worked=5
        )
        
        Pedido.objects.create(
            client=self.cliente,
            tecnico=self.tecnico2,
            scheme=self.scheme,
            hours_worked=20
        )
    
    def test_informe_api_structure(self):
        """Test de la estructura del informe"""
        url = reverse('informe-tecnicos')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('informe', response.data)
        self.assertIn('meta', response.data)
        
        informe = response.data['informe']
        required_fields = [
            'monto_promedio',
            'tecnicos_bajo_promedio', 
            'ultimo_trabajador_monto_bajo',
            'ultimo_trabajador_monto_alto',
            'total_tecnicos',
            'total_horas_sistema',
            'total_pedidos_sistema'
        ]
        
        for field in required_fields:
            self.assertIn(field, informe)


class ManagementCommandTest(TestCase):
    """Tests para los comandos de gestión"""
    
    def test_generar_pedidos_command_exists(self):
        """Test de que el comando existe y es importable"""
        from rapihogar.management.commands.generar_pedidos import Command
        self.assertTrue(Command)
    
    def test_crear_tecnicos_command_exists(self):
        """Test de que el comando crear_tecnicos existe"""
        from rapihogar.management.commands.crear_tecnicos import Command
        self.assertTrue(Command)
