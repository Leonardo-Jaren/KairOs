from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

class AuditoriaBaseModel(models.Model):
    """
    Clase abstracta para la auditoria
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creacion")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de actualizacion")
    
    class Meta:
        abstract = True
     
     
class UsuarioManager(BaseUserManager):
    def create_user(self, correo, nombre, password=None, **extra_fields):
        if not correo:
            raise ValueError('El usuario debe tener un correo electrónico')
        if not nombre:
            raise ValueError("EL usuario debe tener un nombre")
        if not password:
            raise ValueError("El usuario debe tener una contrasena")
        correo = self.normalize_email(correo).lower().strip()
        user = self.model(
            correo=correo, 
            nombre=nombre, 
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, correo, nombre, password=None, **extra_fields):
        extra_fields.setdefault("rol",Usuario.Rol.ADMIN)
        extra_fields.setdefault("activo",True)
        
        return self.create_user(correo, nombre, password, **extra_fields)


class Usuario(AbstractBaseUser,AuditoriaBaseModel):
    """
    Modelo de usuario personalizado que extiende AbstractBaseUser.
    Se usa correo electrónico como identificador principal de autenticación.
    """
    class Rol(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        TECNICO = 'tecnico', 'Tecnico'
        USUARIO = 'usuario' , 'Usuario'
        
    id_usuario = models.AutoField(primary_key=True)

    nombre = models.CharField(
        max_length=100, 
        verbose_name='Nombre completo',)
    
    correo = models.EmailField(
        max_length=100,
        unique=True, 
        verbose_name='Correo electrónico',)
    
    password = models.CharField(
        max_length=255,
        db_column="contrasenia_hash",
        verbose_name="Hash de contrasena"
    )
    
    rol = models.CharField(
        max_length=20, 
        choices=Rol.choices, 
        default=Rol.USUARIO,
        verbose_name='Rol')
    
    activo = models.BooleanField(default=True, verbose_name="Activo")
    last_login = None
    
    objects = UsuarioManager()

    # Usar correo como campo de autenticación
    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        indexes = [
            models.Index(fields=['correo'], name='idx_usuario_correo'),
            models.Index(fields=['rol'], name='idx_usuario_rol'),
        ]
    
    def save(self, *args, **kwargs):
        self.correo = self.correo.lower().strip()
        super().save(*args, **kwargs)
        
    @property
    def is_active(self):
        return self.activo
    
    @property
    def is_staff(self):
        return self.rol == self.Rol.ADMIN
    
    @property
    def is_superuser(self):
        return self.rol == self.Rol.ADMIN
    
    def has_perm(self,perm,obj=None):
        return self.rol == self.Rol.ADMIN
    
    def has_module_perms(self, app_label):
        return self.rol == self.Rol.ADMIN

    def __str__(self):
        return f"{self.nombre} ({self.correo})"


class PerfilTecnico(models.Model):
    """
    Perfil específico para usuarios con rol de técnico.
    Relación 1:1 con Usuario.
    """
    id_tecnico = models.AutoField(primary_key=True)

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_tecnico',
        db_column="id_usuario_fk",
        verbose_name='Usuario',
    )
    area = models.CharField(
        max_length=100,
        verbose_name='Área',
        default= "",
        help_text='Ej: Cedeco, Soporte',
    )

    class Meta:
        db_table = 'perfil_tecnico'
        verbose_name = 'Perfil Técnico'
        verbose_name_plural = 'Perfiles Técnicos'

    def __str__(self):
        return f"Técnico: {self.usuario.nombre} - {self.area}"
