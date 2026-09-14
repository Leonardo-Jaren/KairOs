# Documentación Oficial — KairOs Campus & Labs

Plataforma integral de gestión de infraestructura tecnológica, laboratorios, inventario de hardware, catálogo de software, órdenes de mantenimiento preventivo/correctivo y auditoría del sistema.

---

## 🧭 Índice Rápido de Documentación

### 1. Documentación Técnica de Arquitectura
- ⚙️ **Backend:**
  - [Requerimientos y Arquitectura de Backend](backend/requerimientos_backend.md)
  - [Catálogo Completo de Endpoints de la API REST](backend/api_endpoints.md)
- 🖥️ **Frontend:**
  - [Requerimientos y Arquitectura de Frontend](frontend/requerimientos_frontend.md)
  - [Mapa de Rutas, Layouts y Vistas](frontend/rutas_y_vistas.md)
- 🗄️ **Base de Datos:**
  - [Esquema de Base de Datos y Diagrama ER (Mermaid)](base-de-datos/database_schema.md)
  - [Diccionario de Datos Detallado por Tablas](base-de-datos/diccionario_de_datos.md)

### 2. Especificaciones de Módulos (Requerimientos e Historias)
- 📊 **[Matriz General de Módulos y Documentación](MODULOS.md)**: Tabla central que relaciona cada módulo funcional con su backend, frontend, BD, RF, RNF y HU.
- 📋 **[Requerimientos Funcionales (RF)](requerimientos-funcionales/)**: Reglas y flujos de negocio detallados.
- 🛡️ **[Requerimientos No Funcionales (RNF)](requerimientos-no-funcionales/)**: Criterios de rendimiento, seguridad y disponibilidad.
- 👤 **[Historias de Usuario (HU)](historias-de-usuario/)**: Criterios de aceptación bajo el formato Ágil (Dado / Cuando / Entonces).
- 📝 **[Plantillas Estándar](plantillas/)**: Guías y formatos oficiales para extender la documentación.

### 3. Manual de Usuario con Guías Visuales Paso a Paso
- 📖 **[Manual de Usuario KairOs](manual_usuario/MANUAL_DE_USUARIO.md)**: Guía ilustrada con capturas de pantalla reales del sistema, recuadros rojos y secuencias numeradas ("primero se pone esto, luego se selecciona tal cosa y los campos se rellenan de tal manera").

### 4. Exportación a Documento Word (.docx)
- 📄 El proyecto incluye un script en Python (`scripts/exportar_documentacion_word.py`) que compila los documentos Markdown con sus imágenes y tablas en archivos Word (`.docx`) profesionales listos para presentación ejecutiva o institucional.

---

## 🏛️ Convención de Nomenclatura

```
docs/<carpeta>/<modulo>-<slug>.md
```

Ejemplos:
- `docs/requerimientos-funcionales/equipos-gestionar-equipos.md`
- `docs/historias-de-usuario/autenticacion-login-sesion.md`
- `docs/backend/requerimientos_backend.md`

## 🤝 Reglas de Contribución y Código
Consulte [`CONTRIBUCION-IA.md`](CONTRIBUCION-IA.md) para lineamientos de pull requests, ramas, commits semánticos y arquitectura de desarrollo.
