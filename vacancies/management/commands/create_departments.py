from django.core.management.base import BaseCommand
from vacancies.models import Hospital, Department


class Command(BaseCommand):
    help = 'Cria departamentos para os hospitais existentes'

    def handle(self, *args, **options):
        self.stdout.write('Criando departamentos para os hospitais...')
        
        # Hospital Santa Clara (São Paulo)
        hospital_sp = Hospital.objects.get(name='Hospital Santa Clara')
        
        departments_sp = [
            {
                'name': 'Centro Cirúrgico',
                'description': 'Departamento responsável por procedimentos cirúrgicos'
            },
            {
                'name': 'UTI',
                'description': 'Unidade de Terapia Intensiva para pacientes críticos'
            },
            {
                'name': 'Enfermagem',
                'description': 'Departamento de enfermagem geral'
            },
            {
                'name': 'Medicina Interna',
                'description': 'Departamento de medicina interna e clínica médica'
            },
            {
                'name': 'Pediatria',
                'description': 'Departamento especializado em cuidados infantis'
            },
            {
                'name': 'Cardiologia',
                'description': 'Departamento de cardiologia e cirurgia cardíaca'
            },
            {
                'name': 'Neurologia',
                'description': 'Departamento de neurologia e neurocirurgia'
            },
            {
                'name': 'Ortopedia',
                'description': 'Departamento de ortopedia e traumatologia'
            },
            {
                'name': 'Radiologia',
                'description': 'Departamento de diagnóstico por imagem'
            },
            {
                'name': 'Laboratório',
                'description': 'Departamento de análises clínicas'
            },
            {
                'name': 'Farmácia',
                'description': 'Departamento farmacêutico hospitalar'
            },
            {
                'name': 'Administração',
                'description': 'Departamento administrativo e gestão'
            }
        ]
        
        for dept_data in departments_sp:
            dept, created = Department.objects.get_or_create(
                hospital=hospital_sp,
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            if created:
                self.stdout.write(f'✅ Criado: {dept.name} - {hospital_sp.name}')
            else:
                self.stdout.write(f'⚠️  Já existe: {dept.name} - {hospital_sp.name}')
        
        # Hospital São Lucas (Rio de Janeiro)
        hospital_rj = Hospital.objects.get(name='Hospital São Lucas')
        
        departments_rj = [
            {
                'name': 'Enfermagem',
                'description': 'Departamento de enfermagem geral'
            },
            {
                'name': 'Centro Cirúrgico',
                'description': 'Departamento responsável por procedimentos cirúrgicos'
            },
            {
                'name': 'UTI',
                'description': 'Unidade de Terapia Intensiva para pacientes críticos'
            },
            {
                'name': 'Emergência',
                'description': 'Departamento de emergência e urgência'
            },
            {
                'name': 'Oncologia',
                'description': 'Departamento de oncologia e tratamento do câncer'
            },
            {
                'name': 'Maternidade',
                'description': 'Departamento de obstetrícia e ginecologia'
            },
            {
                'name': 'Psiquiatria',
                'description': 'Departamento de psiquiatria e saúde mental'
            },
            {
                'name': 'Fisioterapia',
                'description': 'Departamento de fisioterapia e reabilitação'
            },
            {
                'name': 'Nutrição',
                'description': 'Departamento de nutrição clínica'
            },
            {
                'name': 'Serviço Social',
                'description': 'Departamento de serviço social hospitalar'
            }
        ]
        
        for dept_data in departments_rj:
            dept, created = Department.objects.get_or_create(
                hospital=hospital_rj,
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            if created:
                self.stdout.write(f'✅ Criado: {dept.name} - {hospital_rj.name}')
            else:
                self.stdout.write(f'⚠️  Já existe: {dept.name} - {hospital_rj.name}')
        
        # Hospital Central (Belo Horizonte)
        hospital_mg = Hospital.objects.get(name='Hospital Central')
        
        departments_mg = [
            {
                'name': 'Centro Cirúrgico',
                'description': 'Departamento responsável por procedimentos cirúrgicos'
            },
            {
                'name': 'UTI',
                'description': 'Unidade de Terapia Intensiva para pacientes críticos'
            },
            {
                'name': 'Enfermagem',
                'description': 'Departamento de enfermagem geral'
            },
            {
                'name': 'Medicina Interna',
                'description': 'Departamento de medicina interna e clínica médica'
            },
            {
                'name': 'Cardiologia',
                'description': 'Departamento de cardiologia e cirurgia cardíaca'
            },
            {
                'name': 'Neurologia',
                'description': 'Departamento de neurologia e neurocirurgia'
            },
            {
                'name': 'Ortopedia',
                'description': 'Departamento de ortopedia e traumatologia'
            },
            {
                'name': 'Radiologia',
                'description': 'Departamento de diagnóstico por imagem'
            },
            {
                'name': 'Laboratório',
                'description': 'Departamento de análises clínicas'
            },
            {
                'name': 'Farmácia',
                'description': 'Departamento farmacêutico hospitalar'
            },
            {
                'name': 'Administração',
                'description': 'Departamento administrativo e gestão'
            },
            {
                'name': 'Recursos Humanos',
                'description': 'Departamento de gestão de pessoas'
            },
            {
                'name': 'TI',
                'description': 'Departamento de tecnologia da informação'
            },
            {
                'name': 'Manutenção',
                'description': 'Departamento de manutenção predial'
            },
            {
                'name': 'Limpeza',
                'description': 'Departamento de serviços gerais'
            }
        ]
        
        for dept_data in departments_mg:
            dept, created = Department.objects.get_or_create(
                hospital=hospital_mg,
                name=dept_data['name'],
                defaults={'description': dept_data['description']}
            )
            if created:
                self.stdout.write(f'✅ Criado: {dept.name} - {hospital_mg.name}')
            else:
                self.stdout.write(f'⚠️  Já existe: {dept.name} - {hospital_mg.name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Departamentos criados com sucesso!\n'
                f'Total de departamentos no sistema: {Department.objects.count()}'
            )
        ) 