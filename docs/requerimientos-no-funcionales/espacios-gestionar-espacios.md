# RNF-ESP-001: Calidad y seguridad de la gestión de espacios

## Arquitectura

- Las vistas delegan reglas al servicio de espacios.
- El acceso ORM se concentra en el repositorio.
- El modelo reutiliza BaseModel para auditoría y borrado lógico.
- Los serializers de lectura, detalle y escritura tienen responsabilidades separadas.

## Seguridad

- Todos los endpoints requieren autenticación JWT.
- Solo administradores pueden modificar información.
- Técnicos tienen acceso exclusivo de lectura.
- Los usuarios regulares no pueden consultar el módulo administrativo.

## Experiencia de usuario

- La interfaz es responsive y usa componentes reutilizables.
- Los estados de carga, vacío, éxito y error son visibles.
- La paleta utiliza las variables centralizadas de Tailwind CSS v4.

## Pruebas

- Repositorio, servicio, permisos y contrato HTTP deben contar con pruebas.
- El composable frontend debe probar carga, validación, creación y desactivación.
