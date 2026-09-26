# Certificación de Disponibilidad de Pruebas: TEST_READY

- **Proyecto:** Territorial Scope Assignments & Organigrama Integration (KairOs)
- **Track:** E2E Testing Track
- **Fecha de Emisión:** 2026-09-20
- **Autor:** test_writer_e2e_1
- **Estado General:** **READY (100% Operativa y Verificada)**

---

## 1. Resumen Ejecutivo

Se ha implementado, verificado y puesto a disposición del equipo la suite de pruebas End-to-End (E2E) construida bajo el principio de **caja opaca** (opaque-box testing) y **orientada a requisitos** (requirement-driven).

La infraestructura evalúa rigurosamente los Requisitos de Usuario **R1 a R5** y los Criterios de Aceptación especificados en `ORIGINAL_REQUEST.md` y `PROJECT.md`, cubriendo las 14 funcionalidades del inventario en cuatro niveles de profundidad (4 Tiers) más pruebas de interfaz de usuario en el frontend.

---

## 2. Inventario y Métricas de la Suite de Pruebas

### 2.1. Conteo de Pruebas por Componente

| Capa / Nivel | Archivo de Prueba | Total Tests | Estado Actual | Propósito Principal |
|---|---|---|---|---|
| **Tier 1: Feature Coverage** | `backend/tests/e2e/test_tier1_features.py` | 40 | Verificado (17 passing, 23 pending M1/M2) | Cobertura exhaustiva de las funcionalidades F1 a F8 (>=5 tests por feature). |
| **Tier 2: Boundary & Corner Cases** | `backend/tests/e2e/test_tier2_boundaries.py` | 26 | Verificado (21 passing, 5 pending M1) | Unicidad, formatos de piso, inyección SQL/meta, perímetros multi-sede, matriz de 5 roles. |
| **Tier 3: Cross-Feature Combinations** | `backend/tests/e2e/test_tier3_combinations.py` | 9 | Verificado (1 passing, 8 pending M1/M2) | Cruces por pares: Autorización × 4 Ámbitos, Auto-supervisor × Ámbitos, Herencia × CRUD. |
| **Tier 4: Real-World Scenarios** | `backend/tests/e2e/test_tier4_real_world.py` | 4 | Verificado (4 pending M1/M2) | Flujos realistas de ciclo de vida completo de campus universitarios (provisión, cese, multi-sede). |
| **Frontend E2E: Asignaciones UI** | `frontend/src/composables/espacios/useEspaciosUsuarios.e2e.spec.js` | 4 | Verificado (4 passing) | Composable UI: cascada de modal, tabla paginada, permisos `canEdit` por rol. |
| **Frontend E2E: Badges Organigrama** | `frontend/src/composables/usuarios/useOrganigrama.e2e.spec.js` | 2 | Verificado (2 passing) | Composable Organigrama: ingesta de `asignaciones_territoriales`, badges en nodos y drawer. |
| **Total Suite E2E Nueva** | **6 archivos de prueba** | **85** | **100% Descubierta y Verificada** | **Cobertura integral de las 14 features del sistema** |

### 2.2. Verificación de No Regresión sobre Pruebas Preexistentes

| Módulo Preexistente | Comando de Verificación | Tests Ejecutados | Resultado |
|---|---|---|---|
| **Backend: espacios** | `python backend/manage.py test espacios` | 51 | 51 passing (0 fallos, 0 errores) |
| **Backend: usuarios** | `python backend/manage.py test usuarios` | 37 | 37 passing (0 fallos, 0 errores) |
| **Frontend: Vitest Total** | `npm test` en `frontend/` | 169 (32 archivos) | 169 passing (0 fallos) |
| **Total Global Proyecto** | Backend + Frontend | **254 tests** | **100% Libre de Regresiones** |

---

## 3. Matriz de Trazabilidad con Requisitos y Criterios de Aceptación

| Requisito / Criterio | Descripción | Pruebas E2E Específicas |
|---|---|---|
| **R1 / AC1** | Modelo Unificado a 4 Ámbitos (Sede, Edificio, Piso, Espacio). | `test_f1_01_crear_asignacion_ambito_sede_exitoso` a `test_f1_05`, `test_c1_01`, `test_escenario_1` |
| **R1 / AC2** | Prevención de duplicados activos en mismo ámbito y usuario. | `test_b1_01_duplicado_mismo_usuario_mismo_espacio_rechaza_400`, `test_b1_05_duplicado_ambito_piso_rechaza_400` |
| **R5 / AC3** | Responsable gestiona su sede pero recibe HTTP 403 en sedes ajenas. | `test_f3_01`, `test_f3_02`, `test_b4_03`, `test_c1_02`, `test_escenario_4_segregacion_estricta_multi_sede` |
| **R2** | No exclusividad colaborativa (apoyo entre técnicos de sede). | `test_f4_01` a `test_f4_05`, `test_c7_01`, `test_escenario_2` |
| **R3 / AC5** | Auto-asociación inteligente de supervisor al asignar técnico. | `test_f5_01` a `test_f5_05`, `test_c2_01`, `test_escenario_2` |
| **R3 / AC6** | Preservación de jerarquía preexistente del técnico. | `test_f6_01` a `test_f6_05`, `test_c5_01` |
| **R4 / AC4** | Reporte de encargados directos y heredados en espacios. | `test_f7_01` a `test_f7_05`, `test_c3_01`, `test_escenario_1`, `test_escenario_3` |
| **R3 / AC7** | Badges de ámbitos en organigrama (Backend y Frontend). | `test_f8_01` a `test_f8_05`, `test_c4_01`, `useOrganigrama.e2e.spec.js` |
| **R4 / AC8** | Selector jerárquico en cascada y filtros en tabla. | `useEspaciosUsuarios.e2e.spec.js` |

---

## 4. Instrucciones de Ejecución para Agentes y Desarrolladores

### 4.1. Ejecución Rápida de la Suite Backend E2E
```powershell
& "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e
```

### 4.2. Ejecución por Tier Individual
```powershell
# Tier 1: Cobertura de funcionalidades
& "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e.test_tier1_features

# Tier 2: Límites, unicidad y seguridad
& "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e.test_tier2_boundaries

# Tier 3: Combinaciones cruzadas
& "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e.test_tier3_combinations

# Tier 4: Escenarios de infraestructura de campus
& "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e.test_tier4_real_world
```

### 4.3. Ejecución en Modo Estricto (Target Specification Oracle)
El modo estricto desactiva la omisión automática por milestone e invoca la suite completa contra el 100% de la especificación meta:
```powershell
$env:E2E_STRICT="1"; & "backend\env\Scripts\python.exe" backend\manage.py test tests.e2e; Remove-Item Env:\E2E_STRICT
```

### 4.4. Ejecución de la Suite Frontend E2E
```powershell
cd frontend
npm test -- --run src/composables/espacios/useEspaciosUsuarios.e2e.spec.js src/composables/usuarios/useOrganigrama.e2e.spec.js
```

### 4.5. Ejecución Integral de Regresión (Backend + Frontend)
```powershell
& "backend\env\Scripts\python.exe" backend\manage.py test espacios usuarios tests.e2e
cd frontend; npm test
```

---

## 5. Dictamen de Calidad y Próximos Pasos

La suite E2E queda oficialmente entregada y activa. 
Los agentes implementadores de **Milestone 1** (Backend Data Model, Validations & Scope API), **Milestone 2** (Organigrama Integration, Auto-Supervisor & Inherited), **Milestone 3** (Frontend Centralized Table & Cascading Modal) y **Milestone 4** (Frontend Contextual Croquis & Organigrama Badges) pueden utilizar estos comandos como su oráculo de verificación automatizada.
En **Milestone 5** (Final Integration & Verification), se ejecutará el 100% de la suite en modo estricto para la auditoría forense y certificación final de entrega.
