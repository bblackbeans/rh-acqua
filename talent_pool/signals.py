from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Avg

from .models import (
    Talent, TalentSkill, TalentRecommendation, TalentNote, TalentTag
)
from applications.models import Application
from vacancies.models import Vacancy, Skill


@receiver(post_save, sender=Application)
def create_talent_from_application(sender, instance, created, **kwargs):
    """
    Cria um perfil de talento quando uma candidatura é aprovada.
    """
    if instance.status == 'approved':
        # Verifica se o candidato já tem um perfil de talento
        candidate = instance.candidate
        talent, created = Talent.objects.get_or_create(
            candidate=candidate,
            defaults={
                'status': 'hired',
                'source': 'application',
                'notes': f'Criado automaticamente a partir da candidatura aprovada para a vaga: {instance.vacancy.title}'
            }
        )
        
        if created:
            # Adiciona habilidades da vaga ao talento
            for skill in instance.vacancy.required_skills.all():
                TalentSkill.objects.create(
                    talent=talent,
                    skill=skill,
                    proficiency=3,  # Nível médio por padrão
                    years_experience=1  # 1 ano por padrão
                )


@receiver(post_save, sender=Vacancy)
def generate_talent_recommendations(sender, instance, created, **kwargs):
    """
    Gera recomendações de talentos para uma nova vaga.
    """
    if created:
        # Este é um placeholder para implementação futura
        # A lógica completa seria implementada em um job assíncrono ou celery task
        pass


@receiver(post_save, sender=TalentSkill)
def update_talent_recommendations(sender, instance, created, **kwargs):
    """
    Atualiza recomendações de talentos quando uma habilidade é adicionada ou atualizada.
    """
    talent = instance.talent
    skill = instance.skill
    
    # Encontra vagas que requerem esta habilidade
    vacancies = Vacancy.objects.filter(required_skills=skill, status='open')
    
    for vacancy in vacancies:
        # Calcula pontuação de compatibilidade
        # Este é um algoritmo simples que pode ser melhorado
        required_skills = vacancy.required_skills.all()
        talent_skills = talent.skills.all()
        
        # Calcula quantas habilidades requeridas o talento possui
        matching_skills = set(required_skills).intersection(set(talent_skills))
        match_percentage = (len(matching_skills) / len(required_skills)) * 100 if required_skills else 0
        
        # Ajusta com base na proficiência
        avg_proficiency = TalentSkill.objects.filter(
            talent=talent, 
            skill__in=required_skills
        ).aggregate(avg=Avg('proficiency'))['avg'] or 0
        
        # Pontuação final (50% correspondência de habilidades, 50% nível de proficiência)
        match_score = int((match_percentage * 0.5) + ((avg_proficiency / 5) * 100 * 0.5))
        
        # Cria ou atualiza recomendação se a pontuação for maior que 50%
        if match_score > 50:
            TalentRecommendation.objects.update_or_create(
                talent=talent,
                vacancy=vacancy,
                defaults={
                    'match_score': match_score,
                    'status': 'pending'
                }
            )


@receiver(post_save, sender=TalentNote)
def update_last_contact_date(sender, instance, created, **kwargs):
    """
    Atualiza a data do último contato quando uma nota é adicionada.
    """
    if created:
        talent = instance.talent
        talent.last_contact_date = timezone.now().date()
        talent.save(update_fields=['last_contact_date'])


@receiver(post_save, sender=TalentTag)
def notify_tag_added(sender, instance, created, **kwargs):
    """
    Notifica quando uma tag é adicionada a um talento.
    """
    if created:
        # Este é um placeholder para implementação futura de notificações
        # Pode ser implementado com Django Channels, e-mail, etc.
        pass
