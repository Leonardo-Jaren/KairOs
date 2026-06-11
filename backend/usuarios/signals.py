from django.db.models.signals import post_save
from django.dispatch import receiver

from usuarios.models import Usuario, PerfilTecnico

@receiver(post_save, sender = Usuario)
def gestionar_perfil_tecnico(sender, instance, created, **kwargs):
    """
    Crear perfil tecnico autoamticamente cuando el rol es 'tecnico'
    Funciona tanto en creacion como en actualizacion de rol
    """
    
    if instance.rol == Usuario.Rol.TECNICO:
        PerfilTecnico.objects.get_or_create(usuario=instance)
        
    