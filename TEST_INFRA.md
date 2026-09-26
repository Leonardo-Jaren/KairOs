# Infraestructura de Pruebas E2E (KairOs)

Este documento especifica la arquitectura, filosofía, inventario y diseño en cuatro niveles (4 Tiers) de la suite de pruebas End-to-End (E2E) para el sistema KairOs, cubriendo la gestión de asignaciones territoriales y su integración jerárquica con el organigrama y permisos por sede.

---

## 1. Filosofía de Pruebas (Test Philosophy)

### 1.1. Principio de Caja Opaca (Opaque-Box Testing)
- Las pruebas interactúan con el sistema exclusivamente a través de sus interfaces públicas (endpoints HTTP/REST de Django REST Framework y contratos reactivos de la interfaz de usuario).
- No se asumen ni se manipulan directamente estados internos ni atributos no expuestos.
- Las aserciones validan contratos de respuesta observables: códigos de estado HTTP (200, 201, 204, 400, 403, 404), esquemas y payloads JSON (relaciones expandidas, campos calculados, mensajes de validación), y persistencia transaccional observable.

### 1.2. Basado en Requisitos Formales (Requirement-Driven)
- Toda prueba deriva directamente de los Requisitos de Usuario **R1 a R5** y los Criterios de Aceptación definidos en `ORIGINAL_REQUEST.md` y `PROJECT.md`.
- Cada prueba incluye trazabilidad explícita al requerimiento y criterio que valida.
- Ninguna prueba se diseña como una fachada complaciente: cada caso evalúa condiciones reales y es capaz de detectar regresiones o incumplimientos de contrato.

### 1.3. Aislamiento e Independencia
- Cada caso de prueba inicializa sus propios datos dentro de una transacción aislada de base de datos (`APITestCase` / `TestCase`), sin acoplamiento temporal ni dependencia del orden de ejecución.
- Al finalizar, el entorno se limpia automáticamente.

### 1.4. Testabilidad Progresiva (Progressive Testability)
- La suite E2E está diseñada para acompañar la evolución del proyecto a través de los milestones (M1 a M5).
- Los casos verifican la presencia de capacidades en el sistema y reportan el estado de cumplimiento:
  - En modo estándar, evalúa las capacidades vigentes de manera limpia y señala componentes pendientes de integración.
  - En modo estricto (`E2E_STRICT=1`), actúa como un oráculo de verificación completo contra la especificación total.

---

## 2. Inventario de Features (14 Features de PROJECT.md)

| # | Feature | Categoría | Requisito Fuente | Descripción de Alto Nivel |
|---|---------|-----------|------------------|---------------------------|
| 1 | **Modelo de Asignación a 4 Ámbitos** | Backend / Datos | R1, AC1 | Extensión de `EspacioUsuario` con soporte para granularidades: `sede`, `edificio`, `piso`, `espacio`, claves foráneas condicionales y unicidad activa. |
| 2 | **CRUD y Serialización de Asignaciones** | Backend / API | R1, AC1 | Operaciones completas (POST, GET paginado/filtrado, PATCH, DELETE lógico) en `/api/v1/espacios/usuarios/`. |
| 3 | **Autorización por Sede y Restricción 403** | Backend / Seguridad | R5, AC3 | Permiso `CanManageEspacioUsuario` que valida pertenencia de sede física para `responsable` y rechaza sedes foráneas con HTTP 403. |
| 4 | **No Exclusividad Colaborativa** | Operativa / Negocio | R2 | Carácter referencial de la asignación: técnicos de la misma sede pueden operar en los espacios sin bloqueos excluyentes. |
| 5 | **Auto-asociación Inteligente de Supervisor** | Backend / Jerarquía | R3, AC5 | Si un técnico con `supervisor=None` es asignado a un ámbito de una sede, se le vincula automáticamente el responsable activo de esa sede. |
| 6 | **Preservación de Jerarquía Existente** | Backend / Jerarquía | R3, AC6 | Si el técnico ya posee supervisor, su línea jerárquica no se modifica al recibir una asignación territorial. Docentes nunca reciben supervisor. |
| 7 | **Reporte de Encargados Heredados** | Backend / Espacios | R4, AC4 | Consulta de detalle y lista de espacios (`/api/v1/espacios/{id}/`) reporta encargados directos y encargados heredados de piso/edificio/sede. |
| 8 | **Badges de Ámbitos en Organigrama (Backend)** | Backend / Organigrama | R3, AC7 | Endpoint `/api/v1/usuarios/organigrama/` inyecta `asignaciones_territoriales` con formato de badge descriptivo por nodo. |
| 9 | **Modal con Selector en Cascada** | Frontend / UI | R4, AC8 | Formulario modal en `EspaciosUsuariosView.vue` con selección de nivel y cascada condicional Sede -> Pabellón -> Piso -> Espacio. |
| 10 | **Tabla Centralizada y Filtros** | Frontend / UI | R4, AC10 | Vista de asignaciones con tabla paginada, filtros por sede, edificio y estado, y renderizado compuesto de la ubicación. |
| 11 | **Permisos en UI (`canEdit` extendido)** | Frontend / Seguridad | R5 | Evaluación de permisos en cliente: habilita edición a `superadmin`, `admin` y `responsable` (en sus sedes), y bloquea a técnicos/docentes. |
| 12 | **Acción Contextual en Croquis/Campus** | Frontend / UI | R4, AC9 | Visualización y asignación contextual del encargado de piso directamente en `CroquisPiso.vue` mediante modal pre-filtrado. |
| 13 | **Badges Territoriales en Nodos de Organigrama** | Frontend / UI | R3, AC7 | Renderizado de badges y chips visuales en los nodos de `OrgChartNode.vue` y panel `OrgUserDrawer.vue`. |
| 14 | **Verificación E2E y Suite de Pruebas** | Calidad / QA | R1-R5, AC11 | Infraestructura automatizada multi-tier, verificación de no regresión y resistencia adversarial. |

---

## 3. Arquitectura y Runner de Pruebas

### 3.1. Estructura de Directorios
```
backend/
└── tests/
    ├── __init__.py
    └── e2e/
        ├── __init__.py
        ├── base.py                   # Utilidades de fixtures, autenticación y aserciones
        ├── test_tier1_features.py     # Tier 1: Cobertura de features (>=5 tests/feature)
        ├── test_tier2_boundaries.py   # Tier 2: Límites, unicidad, formatos y seguridad
        ├── test_tier3_combinations.py # Tier 3: Interacciones cruzadas y matrices de roles
        └── test_tier4_real_world.py   # Tier 4: Flujos de infraestructura de campus completos
frontend/
└── src/
    └── composables/
        ├── espacios/
        │   └── useEspaciosUsuarios.e2e.spec.js # Pruebas E2E de cascada y permisos UI
        └── usuarios/
            └── useOrganigrama.e2e.spec.js      # Pruebas E2E de badges en organigrama
```

### 3.2. Comandos de Ejecución
- **Backend E2E Suite Completa:**
  ```powershell
  & "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e
  ```
- **Backend E2E por Tier:**
  ```powershell
  & "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e.test_tier1_features
  & "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e.test_tier2_boundaries
  & "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e.test_tier3_combinations
  & "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e.test_tier4_real_world
  ```
- **Backend E2E en Modo Estricto:**
  ```powershell
  $env:E2E_STRICT="1"; & "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e; Remove-Item Env:\E2E_STRICT
  ```
- **Frontend E2E Suite:**
  ```powershell
  cd frontend
  npm test -- --run src/composables/espacios/useEspaciosUsuarios.e2e.spec.js src/composables/usuarios/useOrganigrama.e2e.spec.js
  ```
- **Suite Integral de Regresión (Backend + Frontend):**
  ```powershell
  & "backend\env\Scripts\python.exe" backend\manage.py test espacios usuarios tests.e2e
  cd frontend; npm test
  ```

---

## 4. Estructura de la Suite en 4 Tiers

### Tier 1: Feature Coverage (Cobertura de Funcionalidades)
Objetivo: Garantizar que cada una de las funcionalidades asignadas tenga al menos 5 pruebas unitarias/E2E enfocadas en el camino feliz, validación de contrato y respuesta observable.

- **F1: Modelo de Asignación a 4 Ámbitos**
  1. `test_f1_crear_asignacion_ambito_sede_exitoso`: Creación y persistencia de ámbito sede con `local` poblado y campos inferiores nulos.
  2. `test_f1_crear_asignacion_ambito_edificio_exitoso`: Creación y persistencia de ámbito edificio con `local` inferido de edificio.
  3. `test_f1_crear_asignacion_ambito_piso_exitoso`: Creación y persistencia de ámbito piso con edificio y número de nivel.
  4. `test_f1_crear_asignacion_ambito_espacio_compatibilidad`: Creación por espacio con denormalización de relaciones superiores.
  5. `test_f1_auditoria_y_estado_activo_por_defecto`: Verificación de `created_by`, `updated_by`, timestamps y `activo=True`.

- **F2: CRUD y Serialización de Asignaciones**
  1. `test_f2_api_list_paginado_con_metadata`: GET `/api/v1/espacios/usuarios/` con paginación (`count`, `results`).
  2. `test_f2_api_post_creacion_con_entidades_expandidas`: Respuesta 201 contiene usuario, ámbito y ubicación anidados.
  3. `test_f2_api_patch_actualizacion_parcial`: Actualización de tipo de responsabilidad y estado activo.
  4. `test_f2_api_delete_logico`: DELETE responde 204 y marca `is_deleted=True, activo=False`.
  5. `test_f2_api_filtros_por_ambito_y_sede`: Filtrado por query params (`?ambito=piso`, `?local_id=1`).

- **F3: Autorización por Sede y Restricción 403**
  1. `test_f3_responsable_gestiona_propia_sede_exitoso`: Responsable asignado a Sede A crea asignación en Sede A (HTTP 201).
  2. `test_f3_responsable_rechazado_en_sede_ajena_403`: Responsable de Sede A intenta crear en Sede B -> HTTP 403 Forbidden.
  3. `test_f3_tecnico_rechazado_en_escritura_403`: Técnico intenta POST en asignaciones -> HTTP 403.
  4. `test_f3_docente_rechazado_en_escritura_403`: Docente intenta DELETE en asignaciones -> HTTP 403.
  5. `test_f3_superadmin_acceso_universal`: Superadmin y admin crean en cualquier sede sin restricción.

- **F4: No Exclusividad Colaborativa**
  1. `test_f4_tecnico_encargado_no_bloquea_otros_tecnicos`: Múltiples técnicos de la sede pueden consultar el espacio asignado.
  2. `test_f4_coexistencia_de_roles_en_mismo_perimetro`: Convivencia de técnico de piso con docente de aula.
  3. `test_f4_listado_operativo_sede_incluye_todos_los_tecnicos`: Técnicos de sede listan ambientes sin restricción excluyente.
  4. `test_f4_trazabilidad_referencial_de_contacto`: La asignación expone al encargado primario como punto de contacto.
  5. `test_f4_reasignacion_operativa_sin_interrupcion_servicio`: Modificación de asignación mantiene accesibilidad.

- **F5: Auto-asociación Inteligente de Supervisor**
  1. `test_f5_tecnico_sin_supervisor_autoasocia_responsable_sede`: Al asignar técnico con `supervisor=None`, adopta al responsable de la sede.
  2. `test_f5_autoasociacion_desde_asignacion_piso`: Asignación a nivel de piso infiere la sede del edificio y vincula responsable.
  3. `test_f5_autoasociacion_desde_asignacion_espacio`: Asignación a espacio infiere la sede y asocia supervisor.
  4. `test_f5_sede_sin_responsable_no_falla_asignacion`: Si la sede no tiene responsable activo, supervisor queda en `None` sin error.
  5. `test_f5_docente_sin_supervisor_no_adopta_responsable`: Docentes permanecen con `supervisor=None` por regla de negocio.

- **F6: Preservación de Jerarquía Existente**
  1. `test_f6_tecnico_con_supervisor_conserva_su_jefe`: Técnico con supervisor previo no cambia de supervisor al ser asignado.
  2. `test_f6_asignacion_a_segunda_sede_no_altera_jerarquia`: Asignar a un segundo ámbito conserva el supervisor preexistente.
  3. `test_f6_reasignacion_de_responsabilidad_no_muta_supervisor`: Cambiar `tipo_responsabilidad` mantiene supervisor intacto.
  4. `test_f6_inactivacion_de_asignacion_preserva_supervisor`: Desactivar la asignación no elimina la línea de mando establecida.
  5. `test_f6_jerarquia_inmune_a_borrado_logico`: DELETE de la asignación territorial no altera `usuario.supervisor`.

- **F7: Reporte de Encargados Heredados**
  1. `test_f7_espacio_reporta_encargado_directo`: `GET /api/v1/espacios/{id}/` incluye `encargados_directos`.
  2. `test_f7_espacio_hereda_encargado_de_piso`: Espacio sin asignación directa reporta al técnico de piso en `encargados_heredados`.
  3. `test_f7_espacio_hereda_encargado_de_edificio`: Espacio reporta al encargado de edificio con `origen='edificio'`.
  4. `test_f7_espacio_con_encargado_directo_y_heredados`: Coexistencia de directos y heredados simultáneos.
  5. `test_f7_espacio_responsable_operativo_resuelto`: Campo `responsable` selecciona al encargado más específico disponible.

- **F8: Badges de Ámbitos en Organigrama (Backend)**
  1. `test_f8_nodo_organigrama_incluye_asignaciones_territoriales`: Nodo expone colección `asignaciones_territoriales`.
  2. `test_f8_formato_badge_nivel_sede`: Badge texto `"Responsable · {Sede}"`.
  3. `test_f8_formato_badge_nivel_edificio`: Badge texto `"Encargado {Pabellón}"`.
  4. `test_f8_formato_badge_nivel_piso`: Badge texto `"Encargado Piso {N} · {Pabellón}"`.
  5. `test_f8_usuario_con_multiples_asignaciones_multiples_badges`: Usuario con roles en varios ámbitos retorna array con cada badge.

---

### Tier 2: Boundary & Corner Cases (Casos Límite y Esquinas)
Objetivo: Poner a prueba la robustez del sistema ante combinaciones atípicas, límites numéricos, cadenas de texto especiales, seguridad y manejo de estado residual.

- **B1: Unicidad y Concurrencia de Ámbito**
  1. `test_b1_duplicado_mismo_usuario_mismo_piso_rechaza_400`: Error 400 con `"El usuario ya está asignado a este ámbito."`.
  2. `test_b1_mismo_usuario_diferentes_pisos_permitido`: Mismo técnico asignado a Piso 1 y Piso 2 del mismo edificio.
  3. `test_b1_distintos_usuarios_mismo_piso_permitido`: Varios técnicos asignados al mismo piso (colaboración).
  4. `test_b1_reactivacion_de_registro_soft_deleted`: Asignar de nuevo a un usuario eliminado previamente reactiva la fila sin duplicar.
  5. `test_b1_duplicado_con_activo_false_no_colisiona`: Constraint parcial solo restringe registros con `activo=True, is_deleted=False`.

- **B2: Coherencia de Datos por Nivel de Ámbito**
  1. `test_b2_ambito_piso_sin_piso_rechaza_400`: Payload con `ambito='piso'` y `piso=''` retorna HTTP 400.
  2. `test_b2_ambito_piso_sin_edificio_rechaza_400`: Payload con `ambito='piso'` omitiendo `edificio_id` retorna HTTP 400.
  3. `test_b2_ambito_edificio_sin_edificio_rechaza_400`: Payload con `ambito='edificio'` sin `edificio_id` retorna HTTP 400.
  4. `test_b2_ambito_sede_sin_local_rechaza_400`: Payload con `ambito='sede'` sin `local_id` retorna HTTP 400.
  5. `test_b2_espacio_inexistente_retorna_400`: Payload con `espacio_id=99999` retorna HTTP 400.

- **B3: Formato y Escapado de Piso**
  1. `test_b3_piso_con_espacios_en_blanco_se_normaliza`: `" 2 "` se sanea a `"2"`.
  2. `test_b3_piso_no_numerico_rechaza_400`: Valor `"Segundo Piso"` o `"P-2"` rechazado si el validador exige dígitos.
  3. `test_b3_piso_cero_o_sotano`: Tratamiento de piso `"0"` o `"SS"` según reglas del modelo de espacios.
  4. `test_b3_piso_longitud_maxima`: Entrada con longitud en el límite del `CharField(20)`.
  5. `test_b3_inyeccion_caracteres_especiales`: Cadenas con caracteres SQL/HTML meta no causan fallos de integridad.

- **B4: Perímetro de Seguridad Multi-Sede**
  1. `test_b4_responsable_sin_sedes_asignadas_rechaza_403`: Responsable sin ningún `UsuarioSede` no puede crear en ninguna sede.
  2. `test_b4_responsable_con_multiples_sedes_accede_solo_a_las_suyas`: Valida acceso en Sedes 1 y 2, pero bloqueo en Sede 3.
  3. `test_b4_responsable_no_puede_modificar_asignacion_ajena`: PUT/PATCH sobre asignación de sede ajena retorna HTTP 403.
  4. `test_b4_responsable_no_puede_eliminar_asignacion_ajena`: DELETE sobre asignación de sede ajena retorna HTTP 403.
  5. `test_b4_inyeccion_local_id_cruzado_en_espacio`: Enviar `espacio_id` de Sede B con actor de Sede A es detectado y bloqueado (HTTP 403).

- **B5: Matriz de Roles Exhaustiva**
  1. `test_b5_superadmin_full_access`: Crear, listar, editar y borrar sin restricciones.
  2. `test_b5_admin_full_access`: Crear, listar, editar y borrar en cualquier sede.
  3. `test_b5_responsable_scoped_access`: Crear y editar en sedes autorizadas; 403 en sedes ajenas; 403 en catálogo `/opciones/`.
  4. `test_b5_tecnico_read_only`: GET 200, POST 403, PUT 403, DELETE 403.
  5. `test_b5_docente_read_only`: GET 200, POST 403, PUT 403, DELETE 403.
  6. `test_b5_usuario_general_denegado`: Rol `usuario` sin permisos operativos recibe 403 en todo el módulo.

---

### Tier 3: Cross-Feature Combinations (Combinaciones Cruzadas / Cobertura por Pares)
Objetivo: Verificar el comportamiento conjunto cuando múltiples funcionalidades interactúan de manera concurrente o secuencial.

1. `test_c1_responsable_crea_piso_y_autoasocia_supervisor`:
   - Interacción: Feature 3 (Autorización Responsable) × Feature 1 (Ámbito Piso) × Feature 5 (Auto-Supervisor).
   - El responsable crea asignación de piso para un técnico nuevo; el sistema valida la sede, guarda la asignación de piso y enlaza al técnico con el responsable.
2. `test_c2_responsable_ajeno_intenta_asignar_piso_bloqueo_sin_efectos_secundarios`:
   - Interacción: Feature 3 (Bloqueo 403) × Feature 5 (Auto-Supervisor).
   - Verifica que el rechazo HTTP 403 no ejecute modificaciones colaterales ni vincule supervisores.
3. `test_c3_consulta_espacio_con_cadena_completa_de_herencia`:
   - Interacción: Feature 1 (4 Ámbitos) × Feature 7 (Encargados Heredados).
   - Se configuran asignaciones en Sede, Edificio, Piso y Espacio. La consulta del espacio lista la jerarquía completa con precedencia clara.
4. `test_c4_organigrama_refleja_mutaciones_de_asignacion_en_tiempo_real`:
   - Interacción: Feature 2 (CRUD Asignaciones) × Feature 8 (Badges Organigrama).
   - Se crea una asignación de edificio, se consulta organigrama (badge visible), se elimina la asignación (DELETE), se vuelve a consultar (badge removido).
5. `test_c5_traslado_de_tecnico_entre_sedes_preservando_supervisor_anterior`:
   - Interacción: Feature 5 (Auto-Supervisor) × Feature 6 (Preservación Jerarquía) × Feature 1 (Ámbitos).
   - Técnico vinculado a Responsable A en Sede A recibe asignación en Sede B; su supervisor se mantiene como Responsable A sin sobreescritura.
6. `test_c6_reactivacion_soft_delete_con_cambio_de_responsabilidad`:
   - Interacción: Feature 2 (CRUD / Soft Delete) × Feature 1 (Modelo de Asignación).
   - Asignación eliminada de `docente` se recrea como `tecnico`; se reactiva la misma fila actualizando los campos correctamente.
7. `test_c7_concurrencia_operativa_de_dos_tecnicos_en_mismo_piso`:
   - Interacción: Feature 4 (Colaboración) × Feature 1 (Ámbitos) × Feature 7 (Herencia).
   - Dos técnicos asignados al mismo piso reportan en los espacios correspondientes sin conflicto de unicidad.

---

### Tier 4: Real-World Scenarios (Escenarios de Infraestructura Real)
Objetivo: Simular flujos de gestión operativa integrales que reproducen la vida útil de una sede universitaria.

1. **Escenario 1: Provisión Integral de Campus Universitario (Campus Provisioning)**
   - Creación de Sede "Campus Central Huánuco" con dos pabellones ("Pabellón A" de 3 pisos, "Pabellón B" de 2 pisos) y 6 laboratorios.
   - Designación del Responsable de Campus en ámbito `sede`.
   - Asignación de Encargado de Edificio en Pabellón A.
   - Asignación de Técnico Operativo en Piso 2 del Pabellón A.
   - Asignación de Docente de Cátedra en LAB-201.
   - Verificaciones:
     - Persistencia y estados activos de toda la infraestructura.
     - LAB-201 refleja al Docente como directo y al Técnico de Piso y Encargado de Edificio como heredados.
     - Organigrama muestra la estructura de mando y badges jerárquicos correctos en todos los niveles.

2. **Escenario 2: Delegación Operativa y Mantenimiento Colaborativo (Facility Delegation & Teamwork)**
   - El Responsable de Sede delega el Piso 1 al Técnico Tomás (quien no tenía supervisor).
   - Se verifica que Tomás adquiere automáticamente al Responsable como supervisor directo.
   - Surge una incidencia de emergencia en el LAB-102 (Piso 1); el Técnico Carlos (asignado al Piso 2 de la misma sede) asiste a la emergencia.
   - Verificación de no exclusividad: Carlos accede, consulta y opera sin errores de permisos 403, registrando trazabilidad colaborativa.

3. **Escenario 3: Reestructuración y Cese de Encargado de Piso (Restructuring & Decommissioning)**
   - Un técnico renuncia a sus labores de soporte en el Piso 3.
   - El Responsable ejecuta el retiro de la asignación (soft-delete).
   - Verificaciones:
     - La asignación pasa a inactiva y no aparece en listados vigentes.
     - Los laboratorios del Piso 3 dejan de reportar a ese técnico en `encargados_heredados`.
     - El organigrama retira inmediatamente el badge `"Encargado Piso 3"`.
     - Se asigna un nuevo técnico al Piso 3; el espacio actualiza inmediatamente sus encargados heredados.

4. **Escenario 4: Segregación Estricta Multi-Sede (Multi-Campus Boundary Isolation)**
   - Se modelan dos sedes físicamente independientes: Sede Huánuco (Local 1) y Sede Tingo María (Local 2).
   - El Responsable de Huánuco gestiona asignaciones en su campus.
   - El Responsable de Huánuco intenta registrar un técnico en el Pabellón 1 de Tingo María.
   - El sistema bloquea la operación con HTTP 403 Forbidden.
   - El Responsable de Tingo María gestiona su campus de forma autónoma.
   - El endpoint de organigrama filtrado por sede aísla completamente los árboles de mando de cada campus sin filtraciones de datos.

---

## 5. Criterios de Éxito de la Verificación E2E
1. 100% de los casos de prueba compilan y se descubren sin errores sintácticos ni de importación.
2. Cero regresiones sobre las 51 pruebas de `espacios` y 37 pruebas de `usuarios`.
3. Cobertura completa de los 4 Tiers con trazabilidad a los Requisitos R1-R5.
4. Generación y publicación del reporte de disponibilidad `TEST_READY.md`.
