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
**Quiero** reducir y restaurar la barra lateral
**Para** disponer de mas espacio para el contenido cuando lo necesite

## Descripcion

El control se integra en la zona superior de la barra, que conserva una columna compacta con los iconos de navegacion.

## Criterios de aceptacion

- [x] **Dado** que la barra esta expandida, **cuando** pulso su control superior, **entonces** se reduce de forma suave y conserva los iconos.
- [x] **Dado** que la barra esta reducida en escritorio, **cuando** pulso el mismo control, **entonces** vuelve a su ancho completo.
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

- PR: https://github.com/Leonardo-Jaren/KairOs/pull/18
- Issue GitHub: https://github.com/Leonardo-Jaren/KairOs/issues/19
