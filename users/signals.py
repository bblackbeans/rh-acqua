from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .models import User, CandidateProfile, RecruiterProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Cria automaticamente um perfil para o usuário quando ele é criado,
    baseado no seu papel (role).
    """
    if created:
        if instance.role == User.CANDIDATE:
            CandidateProfile.objects.create(user=instance)
        elif instance.role == User.RECRUITER:
            RecruiterProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Salva o perfil do usuário quando o usuário é salvo.
    """
    if instance.role == User.CANDIDATE and hasattr(instance, 'candidate_profile'):
        instance.candidate_profile.save()
    elif instance.role == User.RECRUITER and hasattr(instance, 'recruiter_profile'):
        instance.recruiter_profile.save()
