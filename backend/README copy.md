# 🚀 Backend API — Servidor de Noticias IA

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-05998b.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-336791.svg)
![Redis](https://img.shields.io/badge/Redis-7.2+-dc382d.svg)
![Docker](https://img.shields.io/badge/Docker-24+-2496ed.svg)

Este es el núcleo inteligente del Portal de Noticias de Huánuco. Un backend robusto desarrollado en **FastAPI** que orquesta la ingesta de noticias, el almacenamiento vectorial y la inferencia de IA local para ofrecer una experiencia RAG (Retrieval-Augmented Generation) fluida.

---

## ✨ Características Principales

- 🧠 **RAG Nativo**: Procesamiento de lenguaje natural sobre noticias locales utilizando Ollama.
- 🔍 **Búsqueda Híbrida**: Combinación de búsqueda vectorial (semántica) y palabras clave exactas.
- ⚡ **Streaming SSE**: Respuestas de IA en tiempo real mediante Server-Sent Events.
- 🔄 **Sincronización Automática**: Scrapers especializados para WordPress y sitios locales.
- 🛡️ **Arquitectura Hexagonal**: Código desacoplado, modular y altamente testeable basado en puertos y adaptadores.
- 🚀 **Caché Proactiva**: Integración con Redis para optimizar tiempos de respuesta.

---

## 🏗️ Arquitectura de Software: Hexagonal (Puertos y Adaptadores)

El backend implementa una **Arquitectura Hexagonal (Puertos y Adaptadores)** estricta, lo que garantiza el desacoplamiento completo de la lógica de negocio central (Dominio y Aplicación) frente a la infraestructura técnica y del protocolo HTTP.

```mermaid
flowchart TD
    subgraph "Adaptadores de Entrada (Presentación REST / API)"
        A_Schemas[Schemas de API / Pydantic REST models]
        R_Routers[Routers / Endpoints FastAPI]
        A_Schemas -->|Valida entrada web| R_Routers
    end

    subgraph "Capa de Aplicación"
        B_DTOs[DTOs de Aplicación / Input & Output models]
        B_UC[Casos de Uso / Use Cases]
        B_DTOs -->|Encapsula parámetros| B_UC
    end

    subgraph "Capa de Dominio (Core)"
        D_Entities[Entidades de Dominio / Article, ChatSession...]
        D_Ports[Puertos / Repositories & Services Interfaces]
    end

    subgraph "Adaptadores de Salida (Infraestructura)"
        C_DB[(PostgreSQL + pgvector)]
        C_Cache[(Redis Cache)]
        C_Ollama[Ollama LLM & Embeddings]
    end

    R_Routers -->|Mapea Schema a DTO e invoca| B_DTOs
    B_UC -->|Consulta/Persiste| D_Ports
    B_UC -->|Retorna| D_Entities

    D_Ports -.->|Implementado por| C_DB
    D_Ports -.->|Implementado por| C_Cache
    D_Ports -.->|Implementado por| C_Ollama
```

---

## 🛠️ Tecnologías Utilizadas

### Core & API
- **FastAPI**: Framework web asíncrono de alto rendimiento.
- **SQLAlchemy**: ORM para gestión de base de datos relacional.
- **Pydantic**: Validación de datos y gestión de esquemas.

### Inteligencia Artificial
- **Ollama**: Motor de inferencia local para LLMs (`qwen2.5-coder:1.5b`) y embeddings (`embeddinggemma`).
- **pgvector**: Extensión de PostgreSQL para almacenamiento y búsqueda de vectores.

### Infraestructura
- **PostgreSQL**: Base de datos principal.
- **Redis**: Capa de caché y gestión de estado.
- **Docker & Docker Compose**: Contenedorización completa del entorno.

---

## 🧠 Integración de IA Local

El backend se comunica con una instancia local de Ollama:
- **Embeddings**: Vectorización de títulos y contenido (768 dimensiones).
- **Chat**: Generación de respuestas contextuales con inyección de noticias relevantes.

---

## 🚀 Instalación y Uso

### Requisitos Previos
- Docker y Docker Compose.
- Ollama instalado localmente (con los modelos `qwen2.5-coder:1.5b` y `embeddinggemma`).

### Configuración
1. Copia el archivo de ejemplo de variables de entorno:
   ```bash
   cp .env.example .env
   ```
2. Ajusta las variables según tu entorno local.

### Ejecución con Docker
```bash
docker compose up --build
```

El servidor estará disponible en `http://localhost:8000`. Puedes acceder a la documentación interactiva en `http://localhost:8000/docs`.

---

## 📂 Estructura del Proyecto

```bash
backend/app/
├── main.py             # Punto de entrada de FastAPI.
├── api/                # Adaptadores de entrada (HTTP endpoints & schemas).
├── application/        # Casos de uso de la aplicación (Lógica de negocio).
├── domain/             # Dominio puro (Entidades y puertos/interfaces).
└── infrastructure/     # Adaptadores de salida (Base de datos, Caché, IA y Scrapers).
```
