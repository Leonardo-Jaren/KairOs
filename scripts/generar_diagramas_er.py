import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "docs" / "base-de-datos" / "imagenes"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Macro Diagram: All 14 entities
DIAGRAMA_GENERAL = """
erDiagram
    LOCALES ||--o{ EDIFICIOS : "agrupa (1:N)"
    EDIFICIOS ||--o{ ESPACIOS : "contiene (1:N)"
    ESPACIOS ||--o{ ESPACIOS_USUARIOS : "tiene usuarios (1:N)"
    USUARIOS ||--o{ ESPACIOS_USUARIOS : "asignado en (1:N)"
    USUARIOS ||--o| PERFIL_TECNICO : "tiene (1:1)"
    USUARIOS ||--o{ HISTORIAL : "ejecuta accion (1:N)"
    USUARIOS ||--o{ MANTENIMIENTO : "reporta (1:N)"
    ESPACIOS ||--o{ EQUIPOS : "aloja (1:N)"
    ESPACIOS ||--o{ INCIDENCIAS : "ocurre en (1:N)"
    EQUIPOS ||--o{ COMPONENTES : "posee componentes (1:N)"
    EQUIPOS ||--o{ SOFTWARE_INSTALADO : "tiene instalado (1:N)"
    PRODUCTOS_SOFTWARE ||--o{ SOFTWARE_INSTALADO : "se instala en (1:N)"
    EQUIPOS ||--o{ MANTENIMIENTO : "recibe (1:N)"
    EQUIPOS ||--o{ INCIDENCIAS : "presenta falla (1:N)"
    MANTENIMIENTO ||--o{ TECNICO_MANTENIMIENTO : "asignado a (1:N)"
    PERFIL_TECNICO ||--o{ TECNICO_MANTENIMIENTO : "atiende (1:N)"

    LOCALES {
        bigint id PK
        string codigo UK
        string nombre
        string ciudad
        boolean activo
    }
    EDIFICIOS {
        bigint id PK
        bigint local_id FK
        string codigo UK
        string nombre
        boolean activo
    }
    ESPACIOS {
        bigint id PK
        bigint edificio_id FK
        string codigo_espacio UK
        string tipo
        boolean activo
    }
    ESPACIOS_USUARIOS {
        bigint id PK
        bigint espacio_id FK
        bigint usuario_id FK
        string tipo_responsabilidad
        boolean activo
    }
    USUARIOS {
        bigint id PK
        string username UK
        string nombre
        string correo UK
        string rol
        boolean is_active
    }
    PERFIL_TECNICO {
        bigint id PK
        bigint usuario_id FK "1:1"
        string area
        boolean is_deleted
    }
    EQUIPOS {
        bigint id PK
        bigint espacio_id FK
        string codigo UK
        string numero_serie UK
        string estado
    }
    COMPONENTES {
        bigint id PK
        bigint equipo_id FK
        string tipo
        string numero_serie
    }
    PRODUCTOS_SOFTWARE {
        bigint id PK
        string software
        string tipo_licencia
    }
    SOFTWARE_INSTALADO {
        bigint id PK
        bigint equipo_id FK
        bigint producto_software_id FK
    }
    MANTENIMIENTO {
        bigint id PK
        bigint equipo_id FK
        bigint reportado_por_id FK
        string estado
    }
    TECNICO_MANTENIMIENTO {
        bigint id PK
        bigint mantenimiento_id FK
        bigint tecnico_id FK
    }
    INCIDENCIAS {
        bigint id PK
        bigint espacio_id FK
        bigint equipo_id FK
        string tipo_incidencia
        string estado
    }
    HISTORIAL {
        bigint id PK
        bigint usuario_id FK
        string tipo_evento
    }
"""

# 2. Domain: Usuarios, Perfiles y Auditoria
DIAGRAMA_USUARIOS = """
erDiagram
    USUARIOS ||--o| PERFIL_TECNICO : "tiene perfil (1:1)"
    USUARIOS ||--o{ ESPACIOS_USUARIOS : "asignado a espacios (1:N)"
    USUARIOS ||--o{ HISTORIAL : "registra auditoria (1:N)"

    USUARIOS {
        bigint id PK "Identificador unico"
        string username UK "Nombre de usuario unico"
        string nombre "Nombres del usuario"
        string apellido "Apellidos del usuario"
        string dni "Documento Nacional de Identidad"
        string correo UK "Correo electronico institucional"
        string rol "ADMINISTRADOR / ENCARGADO / DOCENTE / TECNICO"
        boolean is_active "Estado de habilitacion de cuenta"
        datetime created_at "Fecha y hora de registro"
        datetime updated_at "Fecha de ultima modificacion"
    }

    PERFIL_TECNICO {
        bigint id PK "Identificador unico"
        bigint usuario_id FK "Relacion 1 a 1 con USUARIOS"
        string area "Soporte TI / Redes / Mantenimiento Hardware"
        boolean is_deleted "Borrado logico soft delete"
    }

    ESPACIOS_USUARIOS {
        bigint id PK "Identificador unico"
        bigint espacio_id FK "Espacio fisico asignado"
        bigint usuario_id FK "Usuario asignado"
        string tipo_responsabilidad "docente / encargado_lab / jefe_area"
        boolean activo "Asignacion vigente"
        boolean is_deleted "Borrado logico"
    }

    HISTORIAL {
        bigint id PK "Identificador unico de evento"
        bigint usuario_id FK "Usuario ejecutor de la accion"
        datetime fecha "Marca de tiempo del evento"
        string tipo_evento "LOGIN / CREAR / EDITAR / ELIMINAR"
        bigint content_type_id FK "Tabla de entidad afectada"
        integer object_id "ID del registro afectado"
        text descripcion "Detalle explicativo de la operacion"
        jsonb datos_extra "Snapshot JSON de estado anterior y nuevo"
    }
"""

# 3. Domain: Infraestructura Fisica
DIAGRAMA_INFRAESTRUCTURA = """
erDiagram
    LOCALES ||--o{ EDIFICIOS : "agrupa sedes/pabellones (1:N)"
    EDIFICIOS ||--o{ ESPACIOS : "contiene ambientes (1:N)"
    ESPACIOS ||--o{ ESPACIOS_USUARIOS : "responsables asignados (1:N)"

    LOCALES {
        bigint id PK "Identificador unico"
        string codigo UK "Codigo unico de sede (ej. SED-NORTE)"
        string nombre "Nombre del campus o local"
        string ciudad "Ciudad o distrito de ubicacion"
        text descripcion "Notas y detalles de la sede"
        boolean activo "Disponibilidad operativa"
        boolean is_deleted "Borrado logico"
        datetime created_at "Fecha de creacion"
        datetime updated_at "Ultima modificacion"
    }

    EDIFICIOS {
        bigint id PK "Identificador unico"
        bigint local_id FK "Sede/Local continente"
        string codigo UK "Codigo de edificio (ej. PAB-ING)"
        string nombre "Nombre del pabellon o edificio"
        text descripcion "Detalles estructurales"
        boolean activo "Estado operativo"
        jsonb configuracion_croquis "Coordenadas y croquis 2D"
        boolean is_deleted "Borrado logico"
    }

    ESPACIOS {
        bigint id PK "Identificador unico"
        bigint edificio_id FK "Edificio al que pertenece"
        string codigo_espacio UK "Codigo de ambiente (ej. LAB-204)"
        string tipo "laboratorio / aula_computo / taller / servidor"
        string pabellon "Pabellon fisico"
        string piso "Piso o nivel del edificio (1, 2, 3)"
        boolean activo "Habilitado para uso"
        jsonb configuracion_plano "Distribucion 2D de estaciones y mesas"
        boolean is_deleted "Borrado logico"
    }

    ESPACIOS_USUARIOS {
        bigint id PK "Identificador unico"
        bigint espacio_id FK "Espacio fisico"
        bigint usuario_id FK "Usuario asignado"
        string tipo_responsabilidad "Responsabilidad operativa"
        boolean activo "Asignacion activa"
        boolean is_deleted "Borrado logico"
    }
"""

# 4. Domain: Equipamiento y Software
DIAGRAMA_EQUIPAMIENTO = """
erDiagram
    ESPACIOS ||--o{ EQUIPOS : "aloja en estaciones (1:N)"
    EQUIPOS ||--o{ COMPONENTES : "posee componentes (1:N)"
    EQUIPOS ||--o{ SOFTWARE_INSTALADO : "tiene software instalado (1:N)"
    PRODUCTOS_SOFTWARE ||--o{ SOFTWARE_INSTALADO : "catalogo de software (1:N)"

    ESPACIOS {
        bigint id PK "Identificador de ambiente"
        string codigo_espacio UK "Codigo (LAB-101)"
        string tipo "laboratorio / aula"
        boolean activo "Estado operativo"
    }

    EQUIPOS {
        bigint id PK "Identificador unico de equipo"
        bigint espacio_id FK "Ubicacion espacial fisica"
        string codigo UK "Codigo patrimonial institucional"
        string numero_serie UK "Numero de serie del fabricante"
        string numero_mac "Direccion fisica MAC de red"
        string ipv4 "Direccion IP estatica o dinamica"
        string ipv6 "Direccion IPv6 de red"
        string tipo_equipo "computadora / servidor / switch / proyector"
        string marca "Marca comercial (Dell, HP, Lenovo)"
        string modelo "Modelo del equipo"
        string modo_adquisicion "compra / donacion / leasing"
        date fecha_adquisicion "Fecha de compra o ingreso"
        date fecha_renovacion "Fecha proyectada de recambio"
        string estado "operativo / mantenimiento / baja"
        string responsable_usuario "Custodio o responsable"
        boolean is_deleted "Borrado logico"
    }

    COMPONENTES {
        bigint id PK "Identificador unico"
        bigint equipo_id FK "Equipo anfitrion"
        string tipo "procesador / ram / disco / gpu / fuente"
        string marca "Fabricante del componente"
        string modelo "Modelo tecnico"
        string numero_serie "Serie individual"
        string capacidad "ej. 16GB DDR4, 1TB NVMe, i7-12700"
        string estado "operativo / con_fallas / reemplazado"
        text notas "Observaciones tecnicas"
        boolean is_deleted "Borrado logico"
    }

    PRODUCTOS_SOFTWARE {
        bigint id PK "Identificador de software"
        string software "Nombre comercial (MATLAB, AutoCAD)"
        string version "Version (ej. 2024b, v2.1)"
        text descripcion "Proposito y alcance"
        string tipo_licencia "propiedad / suscripcion / gpl_libre"
        integer licencias_totales "Cupo total de licencias disponibles"
        date fecha_expiracion "Vencimiento del licenciamiento"
        decimal costo_anual_total "Costo institucional"
        boolean is_deleted "Borrado logico"
    }

    SOFTWARE_INSTALADO {
        bigint id PK "Identificador unico"
        bigint equipo_id FK "Equipo donde esta instalado"
        bigint producto_software_id FK "Producto del catalogo"
        string numero_licencia_usado "Clave o serial utilizado"
        date fecha_instalacion "Fecha de despliegue en equipo"
        boolean is_deleted "Borrado logico"
    }
"""

# 5. Domain: Mantenimiento e Incidencias
DIAGRAMA_MANTENIMIENTO = """
erDiagram
    ESPACIOS ||--o{ INCIDENCIAS : "ocurre en ambiente (1:N)"
    EQUIPOS ||--o{ INCIDENCIAS : "equipo afectado (1:N)"
    EQUIPOS ||--o{ MANTENIMIENTO : "recibe intervencion (1:N)"
    USUARIOS ||--o{ MANTENIMIENTO : "reportado por (1:N)"
    MANTENIMIENTO ||--o{ TECNICO_MANTENIMIENTO : "asigna cuadrilla (1:N)"
    PERFIL_TECNICO ||--o{ TECNICO_MANTENIMIENTO : "tecnico responsable (1:N)"

    EQUIPOS {
        bigint id PK "Identificador unico"
        bigint espacio_id FK "Espacio donde se ubica"
        string codigo UK "Codigo patrimonial"
        string tipo_equipo "Tipo de hardware"
        string estado "operativo / en_reparacion"
    }

    ESPACIOS {
        bigint id PK "Identificador unico"
        string codigo_espacio UK "Codigo de ambiente"
        string tipo "laboratorio / aula"
    }

    USUARIOS {
        bigint id PK "Identificador unico"
        string username UK "Usuario del sistema"
        string rol "Rol del usuario"
    }

    PERFIL_TECNICO {
        bigint id PK "Identificador unico"
        bigint usuario_id FK "Usuario tecnico"
        string area "Especialidad tecnica"
    }

    INCIDENCIAS {
        bigint id PK "Identificador unico de incidencia"
        bigint espacio_id FK "Ambiente donde se suscita"
        bigint equipo_id FK "Equipo afectado (opcional)"
        string tipo_incidencia "hardware / software / red / energia"
        string estado "reportada / en_atencion / resuelta / descartada"
        text descripcion "Detalle pormenorizado de la falla"
        date fecha_resolucion "Fecha de cierre de la incidencia"
        boolean is_deleted "Borrado logico"
    }

    MANTENIMIENTO {
        bigint id PK "Identificador de orden"
        bigint equipo_id FK "Equipo en servicio"
        bigint reportado_por_id FK "Usuario que apertura orden"
        date fecha "Fecha de ejecucion programada"
        string tipo_mantenimiento "preventivo / correctivo"
        string estado "pendiente / en_proceso / completado / cancelado"
        text descripcion "Alcance del mantenimiento"
        boolean is_deleted "Borrado logico"
    }

    TECNICO_MANTENIMIENTO {
        bigint id PK "Identificador unico"
        bigint mantenimiento_id FK "Orden de mantenimiento"
        bigint tecnico_id FK "Tecnico asignado (PERFIL_TECNICO)"
        boolean is_deleted "Borrado logico"
    }
"""

DIAGRAMAS = [
    {
        "filename": "figura_1_erd_general.png",
        "title": "Figura 1: Diagrama Entidad-Relacion General del Sistema KairOs (Macro)",
        "code": DIAGRAMA_GENERAL,
        "width": 1400,
        "font_size": "13px"
    },
    {
        "filename": "figura_2_erd_usuarios_auditoria.png",
        "title": "Figura 2: Diagrama ER — Modulo de Usuarios, Perfiles Tecnicos y Auditoria",
        "code": DIAGRAMA_USUARIOS,
        "width": 950,
        "font_size": "14px"
    },
    {
        "filename": "figura_3_erd_infraestructura_espacios.png",
        "title": "Figura 3: Diagrama ER — Modulo de Infraestructura Fisica, Sedes y Espacios",
        "code": DIAGRAMA_INFRAESTRUCTURA,
        "width": 950,
        "font_size": "14px"
    },
    {
        "filename": "figura_4_erd_equipos_software.png",
        "title": "Figura 4: Diagrama ER — Modulo de Equipamiento, Componentes y Software",
        "code": DIAGRAMA_EQUIPAMIENTO,
        "width": 1100,
        "font_size": "14px"
    },
    {
        "filename": "figura_5_erd_mantenimiento_incidencias.png",
        "title": "Figura 5: Diagrama ER — Modulo de Mantenimiento e Incidencias Tecnicas",
        "code": DIAGRAMA_MANTENIMIENTO,
        "width": 1150,
        "font_size": "14px"
    }
]

def render_all_diagrams():
    print("==================================================================")
    print("GENERADOR DE DIAGRAMAS ER EN ALTA DEFINICION (PNG) CON PLAYWRIGHT")
    print("==================================================================")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        page = browser.new_page(device_scale_factor=2.5)
        
        for item in DIAGRAMAS:
            fname = item["filename"]
            title = item["title"]
            code = item["code"]
            out_file = OUTPUT_DIR / fname
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    body {{
      background: #FFFFFF;
      margin: 0;
      padding: 24px;
      display: inline-block;
      font-family: 'Segoe UI', Arial, sans-serif;
    }}
    #canvas-box {{
      background: #FFFFFF;
      border: 2px solid #000000;
      border-radius: 8px;
      padding: 24px 28px;
      display: inline-block;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    }}
    .diagram-title-banner {{
      font-family: 'Segoe UI', Arial, sans-serif;
      font-size: 15px;
      font-weight: 700;
      color: #000000;
      border-bottom: 2px solid #000000;
      padding-bottom: 8px;
      margin-bottom: 20px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    svg {{
      font-family: 'Segoe UI', Arial, sans-serif !important;
    }}
    .er.entityBox {{
      stroke: #000000 !important;
      stroke-width: 1.5px !important;
    }}
  </style>
</head>
<body>
  <div id="canvas-box">
    <div class="diagram-title-banner">{title}</div>
    <div class="mermaid">
{code}
    </div>
  </div>
  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'base',
      themeVariables: {{
        primaryColor: '#F8FAFC',
        primaryBorderColor: '#000000',
        primaryTextColor: '#000000',
        lineColor: '#000000',
        secondaryColor: '#F1F5F9',
        tertiaryColor: '#FFFFFF',
        fontSize: '{item["font_size"]}',
        fontFamily: 'Segoe UI, Arial, sans-serif'
      }}
    }});
  </script>
</body>
</html>"""
            
            temp_html = OUTPUT_DIR / f"_temp_{fname}.html"
            temp_html.write_text(html_content, encoding="utf-8")
            
            page.goto(temp_html.as_uri())
            page.wait_for_selector("#canvas-box svg", timeout=25000)
            page.wait_for_timeout(600)
            
            box = page.locator("#canvas-box")
            box.screenshot(path=str(out_file))
            if temp_html.exists():
                temp_html.unlink()
            
            size_kb = out_file.stat().st_size / 1024
            print(f" [OK] {fname} ({size_kb:.1f} KB)")
            
        browser.close()
        
    print("==================================================================")
    print(f"Todos los diagramas han sido generados en: {OUTPUT_DIR.resolve()}")
    print("==================================================================")

if __name__ == "__main__":
    render_all_diagrams()
