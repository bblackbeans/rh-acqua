from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError

from .models import (
    Tag, Category, Attachment, Comment, Dashboard, Widget,
    MenuItem, FAQ, Feedback, Announcement
)


@receiver(pre_save, sender=Tag)
def generate_tag_slug(sender, instance, **kwargs):
    """
    Gera automaticamente um slug para a tag, se não for fornecido.
    """
    if not instance.slug:
        instance.slug = slugify(instance.name)


@receiver(pre_save, sender=Category)
def generate_category_slug(sender, instance, **kwargs):
    """
    Gera automaticamente um slug para a categoria, se não for fornecido.
    """
    if not instance.slug:
        instance.slug = slugify(instance.name)


@receiver(pre_save, sender=Category)
def prevent_circular_reference(sender, instance, **kwargs):
    """
    Impede referências circulares na hierarquia de categorias.
    """
    if instance.parent:
        # Verifica se a categoria pai não é a própria categoria
        if instance.pk and instance.parent.pk == instance.pk:
            raise ValidationError("Uma categoria não pode ser pai dela mesma.")
        
        # Verifica se a categoria pai não é uma subcategoria da categoria atual
        parent = instance.parent
        while parent:
            if parent.parent and parent.parent.pk == instance.pk:
                raise ValidationError("Referência circular detectada na hierarquia de categorias.")
            parent = parent.parent


@receiver(post_save, sender=Dashboard)
def handle_default_dashboard(sender, instance, created, **kwargs):
    """
    Garante que apenas um dashboard seja definido como padrão para cada usuário.
    """
    if instance.is_default:
        # Desativa o flag is_default para outros dashboards do mesmo usuário
        Dashboard.objects.filter(
            owner=instance.owner,
            is_default=True
        ).exclude(pk=instance.pk).update(is_default=False)


@receiver(post_save, sender=MenuItem)
def prevent_menu_circular_reference(sender, instance, **kwargs):
    """
    Impede referências circulares na hierarquia de menus.
    """
    if instance.parent:
        # Verifica se o item pai não é o próprio item
        if instance.pk and instance.parent.pk == instance.pk:
            raise ValidationError("Um item de menu não pode ser pai dele mesmo.")
        
        # Verifica se o item pai não é um subitem do item atual
        parent = instance.parent
        while parent:
            if parent.parent and parent.parent.pk == instance.pk:
                raise ValidationError("Referência circular detectada na hierarquia de menus.")
            parent = parent.parent


@receiver(post_save, sender=Feedback)
def handle_feedback_resolution(sender, instance, **kwargs):
    """
    Atualiza a data de resolução quando o status do feedback é alterado para 'resolvido'.
    """
    if instance.status == 'resolved' and not instance.resolved_at:
        instance.resolved_at = timezone.now()
        # Evita loop infinito de salvamento
        Feedback.objects.filter(pk=instance.pk).update(resolved_at=instance.resolved_at)


@receiver(post_save, sender=Announcement)
def validate_announcement_dates(sender, instance, **kwargs):
    """
    Valida as datas de início e término do anúncio.
    """
    if instance.start_date and instance.end_date and instance.start_date >= instance.end_date:
        raise ValidationError("A data de término deve ser posterior à data de início.")


def log_model_change(sender, instance, created, **kwargs):
    """
    Função auxiliar para registrar alterações em modelos.
    """
    action = 'create' if created else 'update'
    model_name = sender.__name__
    
    # Aqui você pode implementar o registro de logs, se necessário
    # Por exemplo, usando um modelo de log ou enviando para um serviço externo
    pass
