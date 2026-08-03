class AuditableMixin:
    """
    Mixin para BaseService que provee auditoría automática en operaciones CRUD.

    Flujo:
      create() → _do_create() [lógica de negocio] → _audit_on_create() [evento]
      update() → snapshot before → _do_update() → snapshot after → _audit_on_update()
      delete() → _do_delete() [lógica de negocio] → _audit_on_delete() [evento]

    Uso simple: heredar el mixin sin sobreescribir nada → auditoría automática.
    Uso complejo: sobreescribir _do_* para lógica de negocio y _audit_on_* para
    personalizar eventos (tipo, descripción, datos_extra).
    """

    _AUDIT_EXCLUDE = frozenset({
        'password', 'last_login', 'created_at', 'updated_at',
        'updated_by_id', 'created_by_id',
    })

    @property
    def _historial(self):
        if not hasattr(self, '_historial_svc'):
            from historial.services.historial_service import HistorialService
            self._historial_svc = HistorialService()
        return self._historial_svc

    def _modulo(self) -> str:
        return self.repository.model.__name__.lower()

    def _audit_snapshot(self, instance) -> dict:
        result = {}
        for field in instance._meta.fields:
            if field.attname in self._AUDIT_EXCLUDE:
                continue
            value = getattr(instance, field.attname, None)
            label = str(field.verbose_name).capitalize()
            result[label] = str(value) if value is not None else '—'
        return result

    def _audit_detect_changes(self, before: dict, after: dict) -> list:
        return [
            {'campo': campo, 'antes': before[campo], 'despues': after[campo]}
            for campo in before
            if before.get(campo) != after.get(campo)
        ]

    def _audit_registrar(
        self,
        instance,
        tipo_evento: str,
        actor,
        descripcion: str,
        datos_extra: dict | None = None,
    ) -> None:
        self._historial.registrar(
            objeto=instance,
            tipo_evento=tipo_evento,
            usuario=actor,
            descripcion=descripcion,
            datos_extra=datos_extra,
        )

    # ── CRUD público con interceptación de auditoría ───────────────────────────

    def create(self, data: dict, actor=None):
        result = self._do_create(data, actor)
        instance, ctx = result if isinstance(result, tuple) else (result, {})
        self._audit_on_create(instance, data, actor, ctx)
        return instance

    def update(self, id: int, data: dict, actor=None):
        before = self._audit_snapshot(self.get_by_id(id))
        updated = self._do_update(id, data, actor)
        after = self._audit_snapshot(updated)
        cambios = self._audit_detect_changes(before, after)
        self._audit_on_update(cambios, updated, actor)
        return updated

    def delete(self, id: int, actor=None):
        instance = self._do_delete(id, actor)
        self._audit_on_delete(instance, actor)

    # ── Hooks de lógica de negocio (sobreescribir en subclases) ───────────────

    def _do_create(self, data: dict, actor=None):
        return super().create(data)

    def _do_update(self, id: int, data: dict, actor=None):
        return super().update(id, data)

    def _do_delete(self, id: int, actor=None):
        instance = self.get_by_id(id)
        super().delete(id)
        return instance

    # ── Hooks de eventos de auditoría (sobreescribir para personalizar) ────────

    def _audit_on_create(self, instance, data, actor, ctx: dict):
        self._audit_registrar(
            instance,
            f'{self._modulo()}.alta',
            actor,
            f'{str(instance)} registrado.',
        )

    def _audit_on_update(self, cambios: list, instance, actor):
        if cambios:
            self._audit_registrar(
                instance,
                f'{self._modulo()}.actualizacion',
                actor,
                f'{str(instance)} actualizado.',
                datos_extra={'cambios': cambios},
            )

    def _audit_on_delete(self, instance, actor):
        self._audit_registrar(
            instance,
            f'{self._modulo()}.baja',
            actor,
            f'{str(instance)} eliminado.',
        )
