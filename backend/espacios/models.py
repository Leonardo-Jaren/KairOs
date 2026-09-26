from django.conf import settings
from django.db import models
from shared.models import BaseModel


class Local(BaseModel):
    """Representa una sede física donde se agrupan los edificios."""

    TIPO_CHOICES = [
        ('campus', 'Campus'),
        ('sede', 'Sede'),
        ('anexo', 'Anexo'),
        ('otro', 'Otro'),
    ]

    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código del local',
        help_text='Identificador global del local, por ejemplo LOC-01.',
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del local',
    )
    ciudad = models.CharField(
        max_length=100,
        verbose_name='Ciudad del local',
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='sede',
        verbose_name='Tipo de ubicación',
    )
    descripcion = models.TextField(
        blank=True,
        default='',
        verbose_name='Descripción',
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Local activo',
    )

    class Meta:
        db_table = 'locales'
        verbose_name = 'Local'
        verbose_name_plural = 'Locales'
        ordering = ['nombre', 'codigo']
        indexes = [
            models.Index(fields=['codigo'], name='idx_local_codigo'),
            models.Index(fields=['nombre'], name='idx_local_nombre'),
            models.Index(fields=['ciudad'], name='idx_local_ciudad'),
            models.Index(fields=['tipo'], name='idx_local_tipo'),
            models.Index(fields=['activo'], name='idx_local_activo'),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Edificio(BaseModel):
    """Representa un bloque físico que agrupa espacios por piso."""

    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código del edificio',
        help_text='Ej: EDIF-01',
    )
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre del edificio',
        help_text='Ej: Edificio 1',
    )
    descripcion = models.TextField(
        blank=True,
        default='',
        verbose_name='Descripción',
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Edificio activo',
    )
    local = models.ForeignKey(
        Local,
        on_delete=models.PROTECT,
        related_name='edificios',
        null=True,
        blank=True,
        verbose_name='Local',
        help_text='Sede física a la que pertenece el edificio.',
    )
    configuracion_croquis = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Configuración de croquis por piso',
        help_text='Dimensiones, ambientes y pasillos dibujados en cada piso.',
    )

    class Meta:
        db_table = 'edificios'
        verbose_name = 'Edificio'
        verbose_name_plural = 'Edificios'
        ordering = ['nombre', 'codigo']
        indexes = [
            models.Index(fields=['codigo'], name='idx_edificio_codigo'),
            models.Index(fields=['nombre'], name='idx_edificio_nombre'),
            models.Index(fields=['activo'], name='idx_edificio_activo'),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Espacio(BaseModel):
    """
    Espacios físicos: laboratorios, oficinas, aulas, etc.
    Ejemplo de codigo_espacio: LAB-203
    """

    TIPO_CHOICES = [
        ('laboratorio', 'Laboratorio'),
        ('oficina', 'Oficina'),
        ('aula', 'Aula'),
        ('sala_computo', 'Sala de Cómputo'),
        ('otro', 'Otro'),
    ]

    codigo_espacio = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código del espacio',
        help_text='Ej: LAB-203',
    )
    tipo = models.CharField(
        max_length=50,
        choices=TIPO_CHOICES,
        verbose_name='Tipo de espacio',
    )
    pabellon = models.CharField(
        max_length=100,
        verbose_name='Pabellón',
        help_text='Ej: Pabellón 1',
    )
    edificio = models.ForeignKey(
        Edificio,
        on_delete=models.SET_NULL,
        related_name='espacios',
        null=True,
        blank=True,
        verbose_name='Edificio',
        help_text='Bloque físico al que pertenece el espacio.',
    )
    piso = models.CharField(
        max_length=20,
        verbose_name='Piso',
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Espacio activo',
    )
    configuracion_plano = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Configuración del plano',
        help_text='Filas, columnas y posiciones de los equipos dentro del espacio.',
    )

    class Meta:
        db_table = 'espacios'
        verbose_name = 'Espacio'
        verbose_name_plural = 'Espacios'
        ordering = ['codigo_espacio']
        indexes = [
            models.Index(fields=['codigo_espacio'], name='idx_espacio_codigo'),
            models.Index(fields=['tipo'], name='idx_espacio_tipo'),
            models.Index(fields=['pabellon'], name='idx_espacio_pabellon'),
        ]

    def __str__(self):
        return f"{self.codigo_espacio} - {self.get_tipo_display()} ({self.pabellon})"


class EspacioUsuario(BaseModel):
    """
    Relaciona usuarios con los recursos territoriales donde tienen responsabilidad operativa o de supervisión.
    Soporta 4 niveles de granularidad física: Sede, Pabellón/Edificio, Piso y Espacio individual.
    """

    AMBITO_SEDE     = 'sede'
    AMBITO_EDIFICIO = 'edificio'
    AMBITO_PISO     = 'piso'
    AMBITO_ESPACIO  = 'espacio'

    AMBITO_CHOICES = [
        (AMBITO_SEDE,     'Sede'),
        (AMBITO_EDIFICIO, 'Pabellón/Edificio'),
        (AMBITO_PISO,     'Piso'),
        (AMBITO_ESPACIO,  'Espacio individual'),
    ]

    TIPO_RESPONSABILIDAD_CHOICES = [
        ('responsable', 'Responsable'),
        ('tecnico',     'Soporte técnico'),
        ('docente',     'Docente asignado'),
    ]

    ambito = models.CharField(
        max_length=20,
        choices=AMBITO_CHOICES,
        default=AMBITO_ESPACIO,
        verbose_name='Nivel de ámbito territorial',
        db_index=True,
        help_text='Granularidad física de la asignación (sede, edificio, piso, espacio).',
    )
    local = models.ForeignKey(
        Local,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='asignaciones_sede',
        verbose_name='Local / Sede',
        help_text='Referencia a la sede física. Obligatorio si el ámbito es sede.',
    )
    edificio = models.ForeignKey(
        Edificio,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='asignaciones_edificio',
        verbose_name='Edificio / Pabellón',
        help_text='Referencia al edificio o pabellón. Obligatorio si el ámbito es edificio o piso.',
    )
    piso = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name='Piso',
        help_text='Identificador del piso (ej. "1", "2"). Obligatorio si el ámbito es piso.',
    )
    espacio = models.ForeignKey(
        Espacio,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='asignaciones_usuario',
        verbose_name='Espacio individual',
        help_text='Referencia al espacio físico específico. Obligatorio si el ámbito es espacio.',
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='asignaciones_espacio',
        verbose_name='Usuario asignado',
    )
    tipo_responsabilidad = models.CharField(
        max_length=20,
        choices=TIPO_RESPONSABILIDAD_CHOICES,
        default='responsable',
        verbose_name='Tipo de responsabilidad',
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Asignación activa',
    )

    class Meta:
        db_table = 'espacios_usuarios'
        verbose_name = 'Asignación de usuario a ámbito territorial'
        verbose_name_plural = 'Asignaciones de usuarios a ámbitos territoriales'
        ordering = ['espacio__codigo_espacio', 'usuario__nombre']
        constraints = [
            models.UniqueConstraint(
                fields=['local', 'usuario'],
                condition=models.Q(ambito='sede', activo=True, is_deleted=False),
                name='uniq_asig_sede_activa',
            ),
            models.UniqueConstraint(
                fields=['edificio', 'usuario'],
                condition=models.Q(ambito='edificio', activo=True, is_deleted=False),
                name='uniq_asig_edif_activa',
            ),
            models.UniqueConstraint(
                fields=['edificio', 'piso', 'usuario'],
                condition=models.Q(ambito='piso', activo=True, is_deleted=False),
                name='uniq_asig_piso_activa',
            ),
            models.UniqueConstraint(
                fields=['espacio', 'usuario'],
                condition=models.Q(ambito='espacio', activo=True, is_deleted=False),
                name='uniq_asig_espacio_activa',
            ),
        ]
        indexes = [
            models.Index(fields=['espacio', 'activo'], name='idx_asig_esp_activa'),
            models.Index(fields=['usuario', 'activo'], name='idx_asig_usr_activa'),
            models.Index(fields=['ambito', 'activo'], name='idx_asig_amb_activa'),
            models.Index(fields=['local', 'activo'], name='idx_asig_loc_activa'),
            models.Index(fields=['edificio', 'activo'], name='idx_asig_edif_activa'),
            models.Index(fields=['edificio', 'piso', 'activo'], name='idx_asig_edif_piso_act'),
        ]

    def clean(self):
        """
        Valida la coherencia de campos requeridos y excluidos según el ámbito territorial:
        - 'sede': exige 'local'; prohíbe 'edificio', 'piso' y 'espacio'.
        - 'edificio': exige 'edificio'; prohíbe 'piso' y 'espacio'; auto-resuelve o valida 'local'.
        - 'piso': exige 'edificio' y 'piso'; prohíbe 'espacio'; auto-resuelve o valida 'local'.
        - 'espacio': exige 'espacio'; auto-resuelve o valida 'edificio', 'piso' y 'local'.
        """
        super().clean()
        from django.core.exceptions import ValidationError

        errors = {}

        if self.ambito not in dict(self.AMBITO_CHOICES):
            errors['ambito'] = f"Ámbito inválido. Debe ser uno de: {', '.join(dict(self.AMBITO_CHOICES).keys())}."
            raise ValidationError(errors)

        if self.ambito == self.AMBITO_SEDE:
            if not self.local:
                errors['local'] = 'El local/sede es obligatorio para asignaciones de nivel sede.'
            if self.edificio:
                errors['edificio'] = 'Una asignación de nivel sede no debe especificar edificio.'
            if self.piso:
                errors['piso'] = 'Una asignación de nivel sede no debe especificar piso.'
            if self.espacio:
                errors['espacio'] = 'Una asignación de nivel sede no debe especificar espacio individual.'

        elif self.ambito == self.AMBITO_EDIFICIO:
            if not self.edificio:
                errors['edificio'] = 'El edificio es obligatorio para asignaciones de nivel edificio.'
            if self.piso:
                errors['piso'] = 'Una asignación de nivel edificio no debe especificar piso.'
            if self.espacio:
                errors['espacio'] = 'Una asignación de nivel edificio no debe especificar espacio individual.'
            if self.edificio and self.edificio.local:
                if not self.local:
                    self.local = self.edificio.local
                elif self.local != self.edificio.local:
                    errors['local'] = 'El local especificado no coincide con el local del edificio.'

        elif self.ambito == self.AMBITO_PISO:
            if not self.edificio:
                errors['edificio'] = 'El edificio es obligatorio para asignaciones de nivel piso.'
            if not self.piso or not str(self.piso).strip():
                errors['piso'] = 'El piso es obligatorio para asignaciones de nivel piso.'
            if self.espacio:
                errors['espacio'] = 'Una asignación de nivel piso no debe especificar espacio individual.'
            if self.edificio and self.edificio.local:
                if not self.local:
                    self.local = self.edificio.local
                elif self.local != self.edificio.local:
                    errors['local'] = 'El local especificado no coincide con el local del edificio.'

        elif self.ambito == self.AMBITO_ESPACIO:
            if not self.espacio:
                errors['espacio'] = 'El espacio individual es obligatorio para asignaciones de nivel espacio.'
            else:
                if self.espacio.piso:
                    if not self.piso:
                        self.piso = self.espacio.piso
                    elif str(self.piso).strip() != str(self.espacio.piso).strip():
                        errors['piso'] = f'El piso especificado ({self.piso}) no coincide con el del espacio ({self.espacio.piso}).'
                if self.espacio.edificio:
                    if not self.edificio:
                        self.edificio = self.espacio.edificio
                    elif self.edificio != self.espacio.edificio:
                        errors['edificio'] = 'El edificio especificado no coincide con el del espacio.'
                    if self.espacio.edificio.local:
                        if not self.local:
                            self.local = self.espacio.edificio.local
                        elif self.local != self.espacio.edificio.local:
                            errors['local'] = 'El local especificado no coincide con el del espacio.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        """
        Auto-completa campos jerárquicos derivados antes de persistir, permitiendo
        que invocaciones directas como objects.create(espacio=..., usuario=...)
        pueblen consistentemente local, edificio y piso sin requerir clean() explícito.
        """
        if self.ambito == self.AMBITO_ESPACIO and self.espacio:
            if not self.piso and self.espacio.piso:
                self.piso = self.espacio.piso
            if not self.edificio and self.espacio.edificio:
                self.edificio = self.espacio.edificio
            if not self.local and self.edificio and self.edificio.local:
                self.local = self.edificio.local
        elif self.ambito in (self.AMBITO_EDIFICIO, self.AMBITO_PISO) and self.edificio:
            if not self.local and self.edificio.local:
                self.local = self.edificio.local

        super().save(*args, **kwargs)

    def __str__(self):
        """Representación textual segura para cualquier nivel territorial."""
        if self.ambito == self.AMBITO_SEDE:
            nombre = self.local.nombre if self.local else 'Sin sede'
            return f'{self.usuario} - Sede: {nombre}'
        elif self.ambito == self.AMBITO_EDIFICIO:
            nombre = self.edificio.nombre if self.edificio else 'Sin edificio'
            return f'{self.usuario} - Edificio: {nombre}'
        elif self.ambito == self.AMBITO_PISO:
            nombre = self.edificio.nombre if self.edificio else 'Edificio'
            return f'{self.usuario} - {nombre} · Piso {self.piso}'
        elif self.espacio:
            return f'{self.usuario} - {self.espacio.codigo_espacio}'
        return f'{self.usuario} - {self.get_ambito_display()}'

    @property
    def nombre_ambito(self) -> str:
        """Etiqueta compacta descriptiva del recurso físico objetivo."""
        if self.ambito == self.AMBITO_SEDE and self.local:
            return f'Sede {self.local.nombre}'
        elif self.ambito == self.AMBITO_EDIFICIO and self.edificio:
            return f'{self.edificio.nombre}'
        elif self.ambito == self.AMBITO_PISO and self.edificio:
            return f'{self.edificio.nombre} · Piso {self.piso}'
        elif self.ambito == self.AMBITO_ESPACIO and self.espacio:
            return f'{self.espacio.codigo_espacio}'
        return self.get_ambito_display()

    @property
    def badge_texto(self) -> str:
        """Formatea el texto para los badges del organigrama, croquis y vistas."""
        if self.ambito == self.AMBITO_SEDE and self.local:
            return f'{self.get_tipo_responsabilidad_display()} · {self.local.nombre}'
        elif self.ambito == self.AMBITO_EDIFICIO and self.edificio:
            return f'Encargado {self.edificio.nombre}'
        elif self.ambito == self.AMBITO_PISO and self.edificio:
            return f'Encargado Piso {self.piso} · {self.edificio.nombre}'
        elif self.ambito == self.AMBITO_ESPACIO and self.espacio:
            pabellon = self.espacio.pabellon or (self.edificio.nombre if self.edificio else '')
            if pabellon:
                return f'{self.espacio.codigo_espacio} · {pabellon}'
            return self.espacio.codigo_espacio
        return self.get_ambito_display()
