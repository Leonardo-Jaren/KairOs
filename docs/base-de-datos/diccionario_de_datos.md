# Diccionario de Datos — KairOs

Especificación de tablas, campos, tipos de datos, restricciones y reglas de integridad.

---

## 1. Tabla: `usuarios`

Modelo central de usuarios autenticables (`usuarios.Usuario`). Extiende `AbstractUser`.

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único |
| `username` | VarChar(150) | NO | - | Unique | Nombre de usuario interno |
| `nombre` | VarChar(255) | NO | - | - | Nombres completos |
| `apellido` | VarChar(255) | NO | `''` | - | Apellidos completos |
| `dni` | VarChar(8) | SÍ | NULL | Unique | Documento Nacional de Identidad |
| `correo` | VarChar(254) | NO | - | Unique, Index (`idx_usuario_correo`) | Correo institucional (clave de autenticación) |
| `rol` | VarChar(20) | NO | `'usuario'` | Check: `usuario`, `admin`, `tecnico`, `docente` | Nivel de permisos RBAC |
| `is_active` | Boolean | NO | `True` | - | Estado de la cuenta (activo/inactivo) |
| `is_staff` | Boolean | NO | `False` | - | Acceso al panel administrativo de Django |
| `is_superuser` | Boolean | NO | `False` | - | Superusuario con todos los privilegios |
| `last_login` | Timestamp | SÍ | NULL | - | Última fecha/hora de inicio de sesión |
| `created_at` | Timestamp | NO | Auto | - | Fecha de registro |
| `updated_at` | Timestamp | NO | Auto | - | Fecha de última modificación |

---

## 2. Tabla: `perfil_tecnico`

Extensión de perfil para usuarios con rol de soporte técnico (`usuarios.PerfilTecnico`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único |
| `usuario_id` | BigInt | NO | - | FK (`usuarios.id`), 1:1 Unique | Enlace al usuario principal |
| `area` | VarChar(100) | NO | - | - | Área técnica (ej. Cedeco, Redes, Soporte) |
| `is_deleted` | Boolean | NO | `False` | - | Bandera de borrado lógico |
| `created_at` | Timestamp | NO | Auto | - | Fecha de creación |
| `updated_at` | Timestamp | NO | Auto | - | Fecha de modificación |

---

## 3. Tabla: `locales`

Sedes físicas territoriales donde se agrupan los edificios (`espacios.Local`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único del local |
| `codigo` | VarChar(50) | NO | - | Unique, Index (`idx_local_codigo`) | Código único institucional (ej: `LOC-01`) |
| `nombre` | VarChar(100) | NO | - | Index (`idx_local_nombre`) | Nombre de la sede (ej: `Local Central`) |
| `ciudad` | VarChar(100) | NO | - | Index (`idx_local_ciudad`) | Ciudad geográfica (ej: `Huánuco`, `Tingo María`) |
| `descripcion` | Text | NO | `''` | - | Notas y detalles de la sede |
| `activo` | Boolean | NO | `True` | Index (`idx_local_activo`) | Estado operativo del local |
| `is_deleted` | Boolean | NO | `False` | - | Borrado lógico |
| `created_at` | Timestamp | NO | Auto | - | Fecha de registro |
| `updated_at` | Timestamp | NO | Auto | - | Fecha de última modificación |

---

## 4. Tabla: `edificios`

Bloques físicos del campus tecnológico (`espacios.Edificio`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único |
| `codigo` | VarChar(50) | NO | - | Unique, Index (`idx_edificio_codigo`) | Código del edificio (ej: `EDIF-01`) |
| `nombre` | VarChar(100) | NO | - | Index (`idx_edificio_nombre`) | Nombre institucional (ej: `Pabellón 1`) |
| `descripcion` | Text | NO | `''` | - | Notas descriptivas del edificio |
| `activo` | Boolean | NO | `True` | Index (`idx_edificio_activo`) | Disponibilidad operativa del edificio |
| `local_id` | BigInt | SÍ | NULL | FK (`locales.id`, PROTECT) | Sede física a la que pertenece el edificio |
| `configuracion_croquis` | JSONB | NO | `{}` | - | Distribución gráfica por piso (paredes, pasillos) |
| `is_deleted` | Boolean | NO | `False` | - | Borrado lógico |

---

## 5. Tabla: `espacios`

Laboratorios, oficinas, aulas y salas de cómputo (`espacios.Espacio`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único |
| `codigo_espacio` | VarChar(50) | NO | - | Unique, Index (`idx_espacio_codigo`) | Código del espacio (ej: `LAB-203`) |
| `tipo` | VarChar(50) | NO | - | Check: `laboratorio`, `oficina`, `aula`, `sala_computo`, `otro` | Tipo funcional de ambiente |
| `pabellon` | VarChar(100) | NO | - | Index (`idx_espacio_pabellon`) | Nombre textual del pabellón |
| `edificio_id` | BigInt | SÍ | NULL | FK (`edificios.id`, SET NULL) | Bloque estructural al que pertenece |
| `piso` | VarChar(20) | NO | - | - | Nivel de piso (ej. `Piso 2`) |
| `activo` | Boolean | NO | `True` | - | Disponibilidad del espacio |
| `configuracion_plano` | JSONB | NO | `{}` | - | Dimensiones de retícula y coordenadas de PCs |
| `is_deleted` | Boolean | NO | `False` | - | Borrado lógico |

---

## 6. Tabla: `espacios_usuarios`

Asignación y corresponsabilidad de usuarios y docentes en laboratorios (`espacios.EspacioUsuario`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único |
| `espacio_id` | BigInt | NO | - | FK (`espacios.id`, CASCADE) | Espacio asignado |
| `usuario_id` | BigInt | NO | - | FK (`usuarios.id`, CASCADE) | Usuario asignado |
| `tipo_responsabilidad` | VarChar(20) | NO | `'responsable'` | Check: `responsable`, `tecnico`, `docente` | Función del usuario en la sala |
| `activo` | Boolean | NO | `True` | - | Estado de la asignación |
| *Restricción Única* | - | - | - | Unique(`espacio_id`, `usuario_id`) | No duplicar asignación en el mismo espacio |

---

## 7. Tabla: `equipos`

Inventario de terminales y dispositivos de cómputo (`equipos.Equipo`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único |
| `espacio_id` | BigInt | SÍ | NULL | FK (`espacios.id`, SET NULL) | Ubicación física actual |
| `codigo` | VarChar(50) | NO | - | Unique, Index (`idx_equipo_codigo`) | Código de inventario patrimonial |
| `numero_serie` | VarChar(100) | NO | - | Unique, Index (`idx_equipo_serie`) | Número de serie de fábrica |
| `numero_mac` | VarChar(50) | NO | `''` | Index (`idx_equipo_mac`) | Dirección física de red Ethernet/WiFi |
| `ipv4` | GenericIP | SÍ | NULL | - | Dirección IPv4 estática/DHCP |
| `ipv6` | GenericIP | SÍ | NULL | - | Dirección IPv6 |
| `tipo_equipo` | VarChar(30) | NO | - | Check: `desktop`, `laptop`, `servidor`, `impresora`, `proyector`, `monitor`, `otro` | Categoría de hardware |
| `marca` | VarChar(100) | NO | - | - | Marca del fabricante |
| `modelo` | VarChar(100) | NO | - | - | Modelo del equipo |
| `modo_adquisicion`| VarChar(20) | NO | - | Check: `comprado`, `arrendado`, `donado` | Vía de adquisición |
| `fecha_adquisicion`| Date | NO | - | - | Fecha de ingreso patrimonial |
| `fecha_renovacion` | Date | SÍ | NULL | - | Vencimiento de contrato de leasing |
| `estado` | VarChar(20) | NO | `'en_uso'` | Check: `en_uso`, `en_mantenimiento`, `dañado`, `de_baja` | Estado operativo |
| `responsable_usuario`| VarChar(255)| NO | `''` | - | Nombre de usuario responsable directo |
| `is_deleted` | Boolean | NO | `False` | - | Borrado lógico |

---

## 8. Tabla: `componentes`

Componentes internos desmontables (`equipos.Componente`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único |
| `equipo_id` | BigInt | NO | - | FK (`equipos.id`, CASCADE) | Equipo al que pertenece |
| `tipo` | VarChar(30) | NO | - | Check: `cpu`, `ram`, `almacenamiento`, `gpu`, `fuente`, `placa_madre`, `otro` | Tipo de componente |
| `marca` | VarChar(100) | NO | - | - | Fabricante del componente |
| `modelo` | VarChar(100) | NO | - | - | Modelo específico |
| `numero_serie` | VarChar(100) | NO | `''` | - | Serial del componente |
| `capacidad` | VarChar(50) | NO | `''` | - | Capacidad técnica (ej. `16GB DDR4`, `1TB NVMe`) |
| `estado` | VarChar(20) | NO | `'operativo'` | Check: `operativo`, `defectuoso`, `en_revision` | Condición técnica |
| `notas` | Text | NO | `''` | - | Observaciones |
| `is_deleted` | Boolean | NO | `False` | - | Borrado lógico |

---

## 9. Tabla: `productos_software`

Catálogo maestro de aplicaciones y licenciamiento (`software.ProductoSoftware`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único |
| `software` | VarChar(200) | NO | - | Index (`idx_producto_sw_nombre`) | Nombre del software (ej. `AutoCAD`) |
| `version` | VarChar(50) | NO | - | - | Versión del producto (ej. `2024`) |
| `descripcion` | Text | NO | `''` | - | Propósito pedagógico o administrativo |
| `tipo_licencia` | VarChar(30) | NO | - | Check: `perpetua`, `suscripcion`, `oem`, `volumen`, `libre` | Esquema de licenciamiento |
| `licencias_totales` | Integer | NO | `0` | - | Límite contratado de puestos |
| `fecha_expiracion` | Date | SÍ | NULL | - | Vencimiento de la suscripción |
| `costo_anual_total` | Decimal(12,2) | NO | `0.00` | - | Inversión económica asociada |
| *Restricción Única*| - | - | - | Unique(`software`, `version`) | No duplicar software con idéntica versión |
| `is_deleted` | Boolean | NO | `False` | - | Borrado lógico |

---

## 10. Tabla: `software_instalado`

Tabla asociativa de instalaciones de software por equipo (`software.SoftwareInstalado`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único |
| `equipo_id` | BigInt | NO | - | FK (`equipos.id`, CASCADE) | Equipo con la instalación |
| `producto_software_id` | BigInt | NO | - | FK (`productos_software.id`, CASCADE) | Software instalado |
| `numero_licencia_usado`| VarChar(255)| NO | `''` | - | Clave de activación usada en el puesto |
| `fecha_instalacion` | Date | NO | - | - | Fecha en que se instaló |
| *Restricción Única* | - | - | - | Unique(`equipo_id`, `producto_software_id`)| Evita registrar dos veces el mismo software en un PC |
| `is_deleted` | Boolean | NO | `False` | - | Borrado lógico |

---

## 11. Tabla: `mantenimiento`

Órdenes de servicio técnico preventivo y correctivo (`mantenimiento.Mantenimiento`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único del ticket |
| `equipo_id` | BigInt | NO | - | FK (`equipos.id`, CASCADE) | Equipo intervenido |
| `reportado_por_id` | BigInt | SÍ | NULL | FK (`usuarios.id`, SET NULL) | Usuario solicitante |
| `fecha` | Date | NO | - | Index (`idx_mant_fecha`) | Fecha de emisión de la orden |
| `tipo_mantenimiento` | VarChar(20) | NO | - | Check: `preventivo`, `correctivo` | Tipo de intervención técnica |
| `estado` | VarChar(20) | NO | `'pendiente'`| Check: `pendiente`, `en_proceso`, `resuelto`, `cancelado` | Estado de resolución |
| `descripcion` | Text | NO | - | - | Diagnóstico o tareas preventivas |
| `is_deleted` | Boolean | NO | `False` | - | Borrado lógico |

---

## 12. Tabla: `tecnico_mantenimiento`

Asignación de uno o más técnicos a una orden de mantenimiento (`mantenimiento.TecnicoMantenimiento`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único |
| `mantenimiento_id` | BigInt | NO | - | FK (`mantenimiento.id`, CASCADE) | Ticket de mantenimiento |
| `tecnico_id` | BigInt | NO | - | FK (`perfil_tecnico.id`, CASCADE) | Técnico asignado |
| *Restricción Única*| - | - | - | Unique(`mantenimiento_id`, `tecnico_id`) | Un técnico se asigna una sola vez por ticket |
| `is_deleted` | Boolean | NO | `False` | - | Borrado lógico |

---

## 13. Tabla: `incidencias`

Reporte y atención de averías en infraestructura y terminales (`incidencias.Incidencia`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador único |
| `espacio_id` | BigInt | NO | - | FK (`espacios.id`, CASCADE) | Ubicación donde ocurrió la falla |
| `equipo_id` | BigInt | NO | - | FK (`equipos.id`, CASCADE) | Equipo afectado |
| `tipo_incidencia` | VarChar(20) | NO | - | Check: `hardware`, `software` | Naturaleza de la avería |
| `descripcion` | Text | NO | - | - | Detalle de la falla observada |
| `estado` | VarChar(20) | NO | `'pendiente'`| Check: `pendiente`, `en_proceso`, `resuelto` | Ciclo de vida del reporte |
| `fecha_resolucion` | Date | SÍ | NULL | - | Fecha en que se solucionó |
| `is_deleted` | Boolean | NO | `False` | - | Borrado lógico |

---

## 14. Tabla: `historial`

Log inmutable de auditoría global (`historial.Historial`).

| Campo | Tipo SQL | Nulo | Por Defecto | Restricciones / Claves | Descripción |
|-------|----------|------|-------------|------------------------|-------------|
| `id` | BigSerial | NO | Auto | PK | Identificador del registro |
| `usuario_id` | BigInt | SÍ | NULL | FK (`usuarios.id`, SET NULL) | Usuario que ejecutó la mutación |
| `fecha` | Timestamp | NO | Auto | Index (`idx_historial_fecha`) | Marca de tiempo del evento |
| `tipo_evento` | VarChar(100) | NO | - | Index (`idx_historial_tipo`) | Clasificador (ej: `equipo.creado`, `mantenimiento.resuelto`)|
| `content_type_id` | BigInt | NO | - | FK (`django_content_type.id`) | Modelo afectado mediante GenericFK |
| `object_id` | BigInt | NO | - | - | ID numérico del objeto afectado |
| `descripcion` | Text | NO | - | - | Resumen legible en español |
| `datos_extra` | JSONB | SÍ | NULL | - | Payload complementario con datos anteriores y nuevos |
