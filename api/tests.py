from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token

User = get_user_model()


class ApiRootTests(APITestCase):
    """
    Testes para a raiz da API.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.client = APIClient()
        self.url = reverse('api:api_root')
    
    def test_api_root(self):
        """
        Testa a raiz da API.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertIn('version', response.data)
        self.assertIn('documentation', response.data)
        self.assertIn('schema', response.data)
        self.assertIn('timestamp', response.data)
        self.assertEqual(response.data['status'], 'online')


class ApiMetadataTests(APITestCase):
    """
    Testes para os metadados da API.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.client = APIClient()
        self.url = reverse('api:api_metadata')
    
    def test_api_metadata(self):
        """
        Testa os metadados da API.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('name', response.data)
        self.assertIn('version', response.data)
        self.assertIn('description', response.data)
        self.assertIn('environment', response.data)
        self.assertIn('contact', response.data)
        self.assertIn('license', response.data)
        self.assertIn('timestamp', response.data)


class AuthenticationTests(APITestCase):
    """
    Testes para autenticação.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.client = APIClient()
        self.login_url = reverse('api:login')
        self.logout_url = reverse('api:logout')
        self.password_change_url = reverse('api:password_change')
        
        # Cria um usuário para os testes
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Cria um token para o usuário
        self.token = Token.objects.create(user=self.user)
    
    def test_login(self):
        """
        Testa o login.
        """
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_login_invalid_credentials(self):
        """
        Testa o login com credenciais inválidas.
        """
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
    
    def test_logout(self):
        """
        Testa o logout.
        """
        # Autentica o cliente
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        
        # Verifica se o token foi removido
        self.assertFalse(Token.objects.filter(user=self.user).exists())
    
    def test_password_change(self):
        """
        Testa a alteração de senha.
        """
        # Autentica o cliente
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        data = {
            'old_password': 'testpassword',
            'new_password': 'newtestpassword',
            'new_password_confirm': 'newtestpassword'
        }
        
        response = self.client.post(self.password_change_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('token', response.data)
        
        # Verifica se a senha foi alterada
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newtestpassword'))
    
    def test_password_change_invalid_old_password(self):
        """
        Testa a alteração de senha com senha atual inválida.
        """
        # Autentica o cliente
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newtestpassword',
            'new_password_confirm': 'newtestpassword'
        }
        
        response = self.client.post(self.password_change_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('old_password', response.data)
    
    def test_password_change_passwords_dont_match(self):
        """
        Testa a alteração de senha com confirmação inválida.
        """
        # Autentica o cliente
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        data = {
            'old_password': 'testpassword',
            'new_password': 'newtestpassword',
            'new_password_confirm': 'differentpassword'
        }
        
        response = self.client.post(self.password_change_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)


class UserViewSetTests(APITestCase):
    """
    Testes para o ViewSet de usuários.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.client = APIClient()
        
        # Cria um usuário administrador para os testes
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True
        )
        
        # Cria um token para o usuário administrador
        self.admin_token = Token.objects.create(user=self.admin_user)
        
        # Cria um usuário normal para os testes
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='normalpassword'
        )
        
        # Cria um token para o usuário normal
        self.normal_token = Token.objects.create(user=self.normal_user)
        
        # URLs
        self.users_url = reverse('api:user-list')
        self.me_url = reverse('api:user-me')
        self.change_password_url = reverse('api:user-change-password')
    
    def test_list_users_as_admin(self):
        """
        Testa a listagem de usuários como administrador.
        """
        # Autentica o cliente como administrador
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_users_as_normal_user(self):
        """
        Testa a listagem de usuários como usuário normal.
        """
        # Autentica o cliente como usuário normal
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.normal_token.key}')
        
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_user_as_admin(self):
        """
        Testa a criação de usuário como administrador.
        """
        # Autentica o cliente como administrador
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword',
            'password_confirm': 'newpassword'
        }
        
        response = self.client.post(self.users_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['email'], 'new@example.com')
        self.assertEqual(response.data['first_name'], 'New')
        self.assertEqual(response.data['last_name'], 'User')
        
        # Verifica se o usuário foi criado
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_create_user_as_normal_user(self):
        """
        Testa a criação de usuário como usuário normal.
        """
        # Autentica o cliente como usuário normal
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.normal_token.key}')
        
        data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpassword',
            'password_confirm': 'newpassword'
        }
        
        response = self.client.post(self.users_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_me(self):
        """
        Testa a obtenção dos dados do usuário autenticado.
        """
        # Autentica o cliente como usuário normal
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.normal_token.key}')
        
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'normaluser')
        self.assertEqual(response.data['email'], 'normal@example.com')
    
    def test_change_password(self):
        """
        Testa a alteração de senha.
        """
        # Autentica o cliente como usuário normal
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.normal_token.key}')
        
        data = {
            'old_password': 'normalpassword',
            'new_password': 'newnormalpassword',
            'new_password_confirm': 'newnormalpassword'
        }
        
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('token', response.data)
        
        # Verifica se a senha foi alterada
        self.normal_user.refresh_from_db()
        self.assertTrue(self.normal_user.check_password('newnormalpassword'))


class HealthCheckTests(APITestCase):
    """
    Testes para a verificação de saúde da API.
    """
    
    def setUp(self):
        """
        Configuração inicial para os testes.
        """
        self.client = APIClient()
        self.url = reverse('api:health_check')
    
    def test_health_check(self):
        """
        Testa a verificação de saúde da API.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('success', response.data)
        self.assertTrue(response.data['success'])
        self.assertIn('message', response.data)
        self.assertIn('timestamp', response.data)
