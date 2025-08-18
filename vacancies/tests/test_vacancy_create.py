import datetime
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import transaction
from vacancies.models import Vacancy, Hospital, Department, JobCategory, Skill

User = get_user_model()


class VacancyCreateTests(TestCase):
    def setUp(self):
        """Configuração inicial para os testes."""
        # Criar usuário recrutador
        self.user = User.objects.create_user(
            email="maria@teste.com",
            password="testpass123"
        )
        self.user.role = 'recruiter'
        self.user.save()

        # Criar dados necessários
        self.hospital = Hospital.objects.create(
            name="Hospital Teste",
            address="Rua Teste, 123",
            city="São Paulo",
            state="SP",
            zip_code="01234-567",
            phone="(11) 1234-5678"
        )
        
        self.department = Department.objects.create(
            name="Centro Cirúrgico",
            hospital=self.hospital
        )
        
        self.category = JobCategory.objects.create(
            name="Médico"
        )
        
        self.skill1 = Skill.objects.create(
            name="Atendimento ao Paciente"
        )
        
        self.skill2 = Skill.objects.create(
            name="Gestão de Equipe"
        )

    def test_create_vacancy_success(self):
        """Testa criação bem-sucedida de uma vaga."""
        self.client.login(email="maria@teste.com", password="testpass123")
        
        url = reverse("vacancies:vacancy_create")
        data = {
            "title": "Cirurgião Cardiologista",
            "description": "Descrição da vaga de cirurgião",
            "requirements": "Requisitos para a vaga",
            "benefits": "Benefícios oferecidos",
            "hospital": self.hospital.pk,
            "department": self.department.pk,
            "category": self.category.pk,
            "location": "São Paulo, SP",
            "status": "published",
            "contract_type": "full_time",
            "experience_level": "mid",
            "is_remote": False,
            "publication_date": datetime.date.today(),
            "closing_date": datetime.date.today() + datetime.timedelta(days=10),
            "salary_range_min": 1800,
            "salary_range_max": 2800,
            "is_salary_visible": True,
            "skills": [self.skill1.pk, self.skill2.pk],
        }
        
        response = self.client.post(url, data)
        
        # Verifica se a vaga foi criada
        self.assertEqual(Vacancy.objects.count(), 1)
        vacancy = Vacancy.objects.first()
        
        # Verifica os campos principais
        self.assertEqual(vacancy.title, "Cirurgião Cardiologista")
        self.assertEqual(vacancy.recruiter, self.user)
        self.assertEqual(vacancy.hospital, self.hospital)
        self.assertEqual(vacancy.department, self.department)
        self.assertEqual(vacancy.category, self.category)
        
        # Verifica as skills
        self.assertEqual(set(vacancy.skills.values_list("pk", flat=True)), {self.skill1.pk, self.skill2.pk})
        
        # Verifica se foi redirecionado para sucesso
        self.assertIn(response.status_code, [200, 302])

    def test_department_not_in_hospital(self):
        """Testa validação de departamento não pertencente ao hospital."""
        # Criar outro hospital e departamento
        other_hospital = Hospital.objects.create(
            name="Outro Hospital",
            address="Rua Outra, 456",
            city="Rio de Janeiro",
            state="RJ",
            zip_code="20000-000",
            phone="(21) 9876-5432"
        )
        
        other_department = Department.objects.create(
            name="Outro Departamento",
            hospital=other_hospital
        )
        
        self.client.login(email="maria@teste.com", password="testpass123")
        
        url = reverse("vacancies:vacancy_create")
        data = {
            "title": "Teste Validação",
            "description": "Descrição de teste",
            "requirements": "Requisitos de teste",
            "benefits": "Benefícios de teste",
            "hospital": self.hospital.pk,
            "department": other_department.pk,  # Departamento de outro hospital
            "category": self.category.pk,
            "location": "São Paulo, SP",
            "status": "draft",
            "contract_type": "full_time",
            "experience_level": "mid",
            "publication_date": datetime.date.today(),
            "closing_date": datetime.date.today() + datetime.timedelta(days=5),
            "salary_range_min": 1000,
            "salary_range_max": 2000,
            "skills": [self.skill1.pk],
        }
        
        response = self.client.post(url, data)
        
        # Verifica se a vaga NÃO foi criada
        self.assertEqual(Vacancy.objects.count(), 0)
        
        # Verifica se o erro foi exibido
        self.assertContains(response, "O departamento não pertence ao hospital selecionado")

    def test_skills_required(self):
        """Testa que pelo menos uma habilidade é obrigatória."""
        self.client.login(email="maria@teste.com", password="testpass123")
        
        url = reverse("vacancies:vacancy_create")
        data = {
            "title": "Teste Skills",
            "description": "Descrição de teste",
            "requirements": "Requisitos de teste",
            "benefits": "Benefícios de teste",
            "hospital": self.hospital.pk,
            "department": self.department.pk,
            "category": self.category.pk,
            "location": "São Paulo, SP",
            "status": "draft",
            "contract_type": "full_time",
            "experience_level": "mid",
            "publication_date": datetime.date.today(),
            "closing_date": datetime.date.today() + datetime.timedelta(days=5),
            "salary_range_min": 1000,
            "salary_range_max": 2000,
            "skills": [],  # Sem skills
        }
        
        response = self.client.post(url, data)
        
        # Verifica se a vaga NÃO foi criada
        self.assertEqual(Vacancy.objects.count(), 0)
        
        # Verifica se o erro foi exibido
        self.assertContains(response, "Pelo menos uma habilidade deve ser selecionada")

    def test_direct_model_creation(self):
        """Testa criação direta do modelo no banco."""
        with transaction.atomic():
            vacancy = Vacancy.objects.create(
                title="Teste Direto",
                description="Descrição de teste",
                requirements="Requisitos de teste",
                hospital=self.hospital,
                department=self.department,
                location="São Paulo, SP",
                recruiter=self.user,
                status="published",
                contract_type="full_time",
                experience_level="mid"
            )
            
            # Adiciona skills
            vacancy.skills.add(self.skill1, self.skill2)
            
            # Verifica se foi criada
            self.assertEqual(Vacancy.objects.count(), 1)
            self.assertEqual(vacancy.recruiter, self.user)
            self.assertEqual(vacancy.skills.count(), 2)

    def test_form_validation(self):
        """Testa validações do formulário."""
        from vacancies.forms import VacancyForm
        
        # Dados válidos
        valid_data = {
            "title": "Vaga Válida",
            "description": "Descrição válida",
            "requirements": "Requisitos válidos",
            "hospital": self.hospital.pk,
            "department": self.department.pk,
            "location": "São Paulo, SP",
            "status": "published",
            "contract_type": "full_time",
            "experience_level": "mid",
            "skills": [self.skill1.pk],
        }
        
        form = VacancyForm(data=valid_data)
        self.assertTrue(form.is_valid())
        
        # Dados inválidos - departamento de outro hospital
        other_hospital = Hospital.objects.create(
            name="Outro Hospital",
            address="Rua Outra, 789",
            city="Belo Horizonte",
            state="MG",
            zip_code="30000-000",
            phone="(31) 1234-5678"
        )
        
        other_department = Department.objects.create(
            name="Outro Departamento",
            hospital=other_hospital
        )
        
        invalid_data = valid_data.copy()
        invalid_data["department"] = other_department.pk
        
        form = VacancyForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("O departamento não pertence ao hospital selecionado", str(form.errors)) 