from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.http import JsonResponse
from django.urls import reverse

from utils.helpers import (
    format_cpf, format_cnpj, format_cep, format_phone, format_currency,
    format_date, format_datetime, is_valid_cpf, is_valid_cnpj
)
from utils.decorators import require_ajax, require_post, require_role
from utils.validators import validate_cpf, validate_cnpj, validate_cep, validate_phone
from utils.views import validate_cpf as validate_cpf_view, validate_cnpj as validate_cnpj_view, get_cep_info


class HelpersTestCase(TestCase):
    """
    Testes para as funções auxiliares.
    """
    
    def test_format_cpf(self):
        """Testa a formatação de CPF."""
        self.assertEqual(format_cpf('12345678901'), '123.456.789-01')
        self.assertEqual(format_cpf('123.456.789-01'), '123.456.789-01')
        self.assertEqual(format_cpf('123456'), '123456')  # CPF inválido
    
    def test_format_cnpj(self):
        """Testa a formatação de CNPJ."""
        self.assertEqual(format_cnpj('12345678901234'), '12.345.678/9012-34')
        self.assertEqual(format_cnpj('12.345.678/9012-34'), '12.345.678/9012-34')
        self.assertEqual(format_cnpj('123456'), '123456')  # CNPJ inválido
    
    def test_format_cep(self):
        """Testa a formatação de CEP."""
        self.assertEqual(format_cep('12345678'), '12345-678')
        self.assertEqual(format_cep('12345-678'), '12345-678')
        self.assertEqual(format_cep('123456'), '123456')  # CEP inválido
    
    def test_format_phone(self):
        """Testa a formatação de telefone."""
        self.assertEqual(format_phone('11987654321'), '(11) 98765-4321')
        self.assertEqual(format_phone('1187654321'), '(11) 8765-4321')
        self.assertEqual(format_phone('987654321'), '98765-4321')
        self.assertEqual(format_phone('87654321'), '8765-4321')
        self.assertEqual(format_phone('123456'), '123456')  # Telefone inválido
    
    def test_format_currency(self):
        """Testa a formatação de valores monetários."""
        self.assertEqual(format_currency(1234.56), 'R$ 1.234,56')
        self.assertEqual(format_currency(1234.56, 'US$'), 'US$ 1.234,56')
        self.assertEqual(format_currency(0), 'R$ 0,00')
    
    def test_format_date(self):
        """Testa a formatação de datas."""
        from datetime import date
        self.assertEqual(format_date(date(2023, 1, 31)), '31/01/2023')
        self.assertEqual(format_date(date(2023, 1, 31), '%Y-%m-%d'), '2023-01-31')
        self.assertEqual(format_date('2023-01-31'), '31/01/2023')
        self.assertEqual(format_date(None), '')
    
    def test_format_datetime(self):
        """Testa a formatação de datetimes."""
        from datetime import datetime
        self.assertEqual(format_datetime(datetime(2023, 1, 31, 12, 30)), '31/01/2023 12:30')
        self.assertEqual(format_datetime(datetime(2023, 1, 31, 12, 30), '%Y-%m-%d %H:%M'), '2023-01-31 12:30')
        self.assertEqual(format_datetime('2023-01-31T12:30:00'), '31/01/2023 12:30')
        self.assertEqual(format_datetime(None), '')
    
    def test_is_valid_cpf(self):
        """Testa a validação de CPF."""
        self.assertTrue(is_valid_cpf('52998224725'))  # CPF válido
        self.assertTrue(is_valid_cpf('529.982.247-25'))  # CPF válido formatado
        self.assertFalse(is_valid_cpf('11111111111'))  # CPF inválido (dígitos repetidos)
        self.assertFalse(is_valid_cpf('12345678901'))  # CPF inválido
        self.assertFalse(is_valid_cpf('123456'))  # CPF inválido (tamanho incorreto)
    
    def test_is_valid_cnpj(self):
        """Testa a validação de CNPJ."""
        self.assertTrue(is_valid_cnpj('33400689000109'))  # CNPJ válido
        self.assertTrue(is_valid_cnpj('33.400.689/0001-09'))  # CNPJ válido formatado
        self.assertFalse(is_valid_cnpj('11111111111111'))  # CNPJ inválido (dígitos repetidos)
        self.assertFalse(is_valid_cnpj('12345678901234'))  # CNPJ inválido
        self.assertFalse(is_valid_cnpj('123456'))  # CNPJ inválido (tamanho incorreto)


class DecoratorsTestCase(TestCase):
    """
    Testes para os decoradores.
    """
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
        
        # Cria um perfil para o usuário
        from django.db import models
        
        class Profile(models.Model):
            user = models.OneToOneField(User, on_delete=models.CASCADE)
            role = models.CharField(max_length=20, default='user')
        
        self.user.profile = Profile(user=self.user, role='user')
    
    def test_require_ajax(self):
        """Testa o decorador require_ajax."""
        @require_ajax
        def test_view(request):
            return JsonResponse({'success': True})
        
        # Requisição AJAX
        request = self.factory.get('/test/')
        request.headers = {'x-requested-with': 'XMLHttpRequest'}
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
        
        # Requisição não-AJAX
        request = self.factory.get('/test/')
        request.headers = {}
        response = test_view(request)
        self.assertEqual(response.status_code, 400)
    
    def test_require_post(self):
        """Testa o decorador require_post."""
        @require_post
        def test_view(request):
            return JsonResponse({'success': True})
        
        # Requisição POST
        request = self.factory.post('/test/')
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
        
        # Requisição GET
        request = self.factory.get('/test/')
        response = test_view(request)
        self.assertEqual(response.status_code, 405)
    
    def test_require_role(self):
        """Testa o decorador require_role."""
        @require_role(['admin'])
        def test_view(request):
            return JsonResponse({'success': True})
        
        # Usuário não autenticado
        request = self.factory.get('/test/')
        request.user = AnonymousUser()
        response = test_view(request)
        self.assertEqual(response.status_code, 302)  # Redirecionamento para login
        
        # Usuário autenticado, mas sem o perfil correto
        request = self.factory.get('/test/')
        request.user = self.user
        response = test_view(request)
        self.assertEqual(response.status_code, 302)  # Redirecionamento para dashboard
        
        # Usuário autenticado com o perfil correto
        request = self.factory.get('/test/')
        request.user = self.user
        request.user.profile.role = 'admin'
        response = test_view(request)
        self.assertEqual(response.status_code, 200)


class ValidatorsTestCase(TestCase):
    """
    Testes para os validadores.
    """
    
    def test_validate_cpf(self):
        """Testa o validador de CPF."""
        from django.core.exceptions import ValidationError
        
        # CPF válido
        validate_cpf('52998224725')
        validate_cpf('529.982.247-25')
        
        # CPF inválido
        with self.assertRaises(ValidationError):
            validate_cpf('11111111111')
        
        with self.assertRaises(ValidationError):
            validate_cpf('12345678901')
        
        with self.assertRaises(ValidationError):
            validate_cpf('123456')
    
    def test_validate_cnpj(self):
        """Testa o validador de CNPJ."""
        from django.core.exceptions import ValidationError
        
        # CNPJ válido
        validate_cnpj('33400689000109')
        validate_cnpj('33.400.689/0001-09')
        
        # CNPJ inválido
        with self.assertRaises(ValidationError):
            validate_cnpj('11111111111111')
        
        with self.assertRaises(ValidationError):
            validate_cnpj('12345678901234')
        
        with self.assertRaises(ValidationError):
            validate_cnpj('123456')
    
    def test_validate_cep(self):
        """Testa o validador de CEP."""
        from django.core.exceptions import ValidationError
        
        # CEP válido
        validate_cep('12345678')
        validate_cep('12345-678')
        
        # CEP inválido
        with self.assertRaises(ValidationError):
            validate_cep('123456')
        
        with self.assertRaises(ValidationError):
            validate_cep('1234567')
        
        with self.assertRaises(ValidationError):
            validate_cep('123456789')
    
    def test_validate_phone(self):
        """Testa o validador de telefone."""
        from django.core.exceptions import ValidationError
        
        # Telefone válido
        validate_phone('11987654321')
        validate_phone('1187654321')
        validate_phone('(11) 98765-4321')
        validate_phone('(11) 8765-4321')
        
        # Telefone inválido
        with self.assertRaises(ValidationError):
            validate_phone('123456')
        
        with self.assertRaises(ValidationError):
            validate_phone('123456789')
        
        with self.assertRaises(ValidationError):
            validate_phone('123456789012')


class ViewsTestCase(TestCase):
    """
    Testes para as views.
    """
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='12345')
    
    def test_validate_cpf_view(self):
        """Testa a view de validação de CPF."""
        # Requisição AJAX com CPF válido
        request = self.factory.get('/utils/validate/cpf/', {'cpf': '52998224725'})
        request.user = self.user
        request.headers = {'x-requested-with': 'XMLHttpRequest'}
        response = validate_cpf_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'is_valid': True})
        
        # Requisição AJAX com CPF inválido
        request = self.factory.get('/utils/validate/cpf/', {'cpf': '12345678901'})
        request.user = self.user
        request.headers = {'x-requested-with': 'XMLHttpRequest'}
        response = validate_cpf_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'is_valid': False})
    
    def test_validate_cnpj_view(self):
        """Testa a view de validação de CNPJ."""
        # Requisição AJAX com CNPJ válido
        request = self.factory.get('/utils/validate/cnpj/', {'cnpj': '33400689000109'})
        request.user = self.user
        request.headers = {'x-requested-with': 'XMLHttpRequest'}
        response = validate_cnpj_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'is_valid': True})
        
        # Requisição AJAX com CNPJ inválido
        request = self.factory.get('/utils/validate/cnpj/', {'cnpj': '12345678901234'})
        request.user = self.user
        request.headers = {'x-requested-with': 'XMLHttpRequest'}
        response = validate_cnpj_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'is_valid': False})
    
    def test_get_cep_info(self):
        """Testa a view de obtenção de informações de CEP."""
        # Este teste requer mock para não depender de API externa
        import unittest.mock as mock
        
        # Mock da resposta da API
        mock_response = mock.Mock()
        mock_response.json.return_value = {
            'cep': '01001-000',
            'logradouro': 'Praça da Sé',
            'complemento': 'lado ímpar',
            'bairro': 'Sé',
            'localidade': 'São Paulo',
            'uf': 'SP',
        }
        
        # Requisição AJAX com CEP válido
        with mock.patch('requests.get', return_value=mock_response):
            request = self.factory.get('/utils/cep-info/', {'cep': '01001000'})
            request.user = self.user
            request.headers = {'x-requested-with': 'XMLHttpRequest'}
            response = get_cep_info(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['cidade'], 'São Paulo')
            self.assertEqual(response.json()['estado'], 'SP')
        
        # Requisição AJAX com CEP inválido
        request = self.factory.get('/utils/cep-info/', {'cep': '123456'})
        request.user = self.user
        request.headers = {'x-requested-with': 'XMLHttpRequest'}
        response = get_cep_info(request)
        self.assertEqual(response.status_code, 400)
