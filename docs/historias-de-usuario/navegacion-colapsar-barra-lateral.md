# HU-NAVEGACION-001: Controlar la barra lateral

| Campo | Valor |
|-------|-------|
| Modulo | Navegacion |
| Prioridad | Media |
| Fecha | 2026-08-17 |
| Autor | Leonardo Jaren |
| Estado | En revision |

## Historia

**Como** usuario autenticado  
**Quiero** cerrar y restaurar la barra lateral  
**Para** disponer de mas espacio para el contenido cuando lo necesite

## Descripcion

El control se integra en la zona superior de la barra y mantiene disponible una forma visible de restaurarla.

## Criterios de aceptacion

- [x] **Dado** que la barra esta visible, **cuando** pulso su control superior, **entonces** se oculta de forma suave.
- [x] **Dado** que la barra esta oculta en escritorio, **cuando** pulso el control del encabezado principal, **entonces** vuelve a mostrarse.
- [x] La navegacion movil conserva su comportamiento actual.

## Alcance tecnico

| Capa | Archivos / endpoints |
|------|----------------------|
| Layout | `frontend/src/layouts/DashboardLayout.vue` |
| Pruebas | `frontend/src/layouts/DashboardLayout.spec.js` |
| API | N/A |

## RF / RNF relacionados

- RF: `RF-NAVEGACION-001`
- RNF: `RNF-NAVEGACION-001`

## Notas de implementacion

Se reutilizan `PanelLeftClose` y `PanelLeftOpen` de Lucide y las variables visuales existentes de KairOs.

## Enlaces

- PR: Pendiente de creacion
- Issue GitHub: Pendiente de creacion
