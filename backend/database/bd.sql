-- ============================================================
--  TIPOS ENUMERADOS
-- ============================================================

CREATE TYPE estado_equipo AS ENUM (
    'no usado',
    'en uso',
    'en mantenimiento',
    'dañado'
);

CREATE TYPE estado_mantenimiento AS ENUM (
    'pendiente',
    'resuelto'
);

CREATE TYPE estado_incidencia AS ENUM (
    'pendiente',      -- recién reportada, sin atender
    'en_revision',    -- asignada a un técnico
    'resuelta',       -- técnico registró solución
    'cerrada'         -- confirmada y archivada por responsable
);

CREATE TYPE prioridad_incidencia AS ENUM (
    'baja',
    'media',
    'alta',
    'critica'
);

CREATE TYPE tipo_rol AS ENUM (
    'admin',
    'tecnico',
    'usuario'
);

CREATE TYPE accion_auditoria AS ENUM (
    'crear',
    'actualizar',
    'eliminar'
);


-- ============================================================
--  PABELLONES
--  Cada pabellón declara cuántos pisos tiene, dado que
--  la universidad cuenta con 7 pabellones de distintas alturas.
-- ============================================================

CREATE TABLE pabellones (
    id_pabellon  SERIAL       PRIMARY KEY,
    nombre       VARCHAR(100) NOT NULL UNIQUE,  -- "Pabellón A", "Pabellón Central", etc.
    descripcion  TEXT,
    total_pisos  INT          NOT NULL DEFAULT 1
);


-- ============================================================
--  ESPACIOS
--  Aulas, laboratorios, oficinas, etc. dentro de un pabellón.
-- ============================================================

CREATE TABLE espacios (
    id_espacio      SERIAL      PRIMARY KEY,
    codigo_espacio  VARCHAR(50) NOT NULL UNIQUE,
    id_pabellon_fk  INT         REFERENCES pabellones(id_pabellon) ON DELETE SET NULL,
    piso            VARCHAR(20),
    tipo            VARCHAR(50),           -- "Laboratorio", "Aula", "Oficina", etc.
    capacidad       INT,                   -- cantidad de puestos/equipos que admite
    descripcion     TEXT
);


-- ============================================================
--  USUARIOS
-- ============================================================

CREATE TABLE usuarios (
    id_usuario       SERIAL       PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    correo           VARCHAR(100) NOT NULL UNIQUE,
    contrasenia_hash VARCHAR(255) NOT NULL,
    rol              tipo_rol     DEFAULT 'usuario',
    activo           BOOLEAN      DEFAULT TRUE,
    created_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
--  PERFIL TÉCNICO
--  Extiende usuarios cuyo rol = 'tecnico'.
-- ============================================================

CREATE TABLE perfil_tecnico (
    id_tecnico     SERIAL PRIMARY KEY,
    id_usuario_fk  INT    UNIQUE REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    area           VARCHAR(100) DEFAULT ''
);


-- ============================================================
--  EQUIPOS
-- ============================================================

CREATE TABLE equipos (
    id_equipo          SERIAL      PRIMARY KEY,
    id_espacio_fk      INT         REFERENCES espacios(id_espacio)  ON DELETE SET NULL,
    codigo             VARCHAR(100) NOT NULL UNIQUE,
    numero_serie       VARCHAR(100),
    numero_mac         VARCHAR(100),
    tipo_equipo        VARCHAR(50),
    marca              VARCHAR(100),
    modelo             VARCHAR(100),
    modo_adquisicion   VARCHAR(100),
    fecha_adquisicion  DATE,
    fecha_renovacion   DATE,
    estado             estado_equipo DEFAULT 'no usado',
    id_responsable_fk  INT         REFERENCES usuarios(id_usuario)  ON DELETE SET NULL
);


-- ============================================================
--  COMPONENTES
--  Piezas físicas de un equipo (RAM, GPU, disco, etc.).
-- ============================================================

CREATE TABLE componentes (
    id_componente  SERIAL PRIMARY KEY,
    id_equipo_fk   INT    REFERENCES equipos(id_equipo) ON DELETE CASCADE,
    tipo           VARCHAR(50),
    modelo         VARCHAR(50),
    numero_serie   VARCHAR(100),   -- trazabilidad individual de cada componente
    descripcion    TEXT
);


-- ============================================================
--  PRODUCTOS SOFTWARE
-- ============================================================

CREATE TABLE productos_software (
    id_producto_software  SERIAL       PRIMARY KEY,
    software              VARCHAR(255) NOT NULL,
    version               VARCHAR(50),
    descripcion           TEXT,
    tipo_licencia         VARCHAR(100),
    licencias_totales     INT          DEFAULT 0,
    fecha_expiracion      DATE,
    costo_anual_total     DECIMAL(12,2),
    UNIQUE(software, version)
);


-- ============================================================
--  SOFTWARE INSTALADO
-- ============================================================

CREATE TABLE software_instalado (
    id_instalacion          SERIAL PRIMARY KEY,
    id_equipo_fk            INT    REFERENCES equipos(id_equipo)                       ON DELETE CASCADE,
    id_producto_software_fk INT    REFERENCES productos_software(id_producto_software) ON DELETE CASCADE,
    numero_licencia_usado   VARCHAR(255),
    fecha_instalacion       DATE   DEFAULT CURRENT_DATE,
    UNIQUE(id_equipo_fk, id_producto_software_fk)
);


-- ============================================================
--  MANTENIMIENTO
-- ============================================================

CREATE TABLE mantenimiento (
    id_mantenimiento      SERIAL             PRIMARY KEY,
    id_equipo_fk          INT                REFERENCES equipos(id_equipo)   ON DELETE CASCADE,
    fecha_inicio          DATE               DEFAULT CURRENT_DATE,
    fecha_cierre          DATE,                                               -- se llena al resolver
    tipo_mantenimiento    VARCHAR(50),                                        -- "Preventivo", "Correctivo"
    estado                estado_mantenimiento DEFAULT 'pendiente',
    descripcion           TEXT,
    observaciones_cierre  TEXT,                                               -- notas del técnico al cerrar
    id_usuario_cierre_fk  INT                REFERENCES usuarios(id_usuario) ON DELETE SET NULL
);


-- ============================================================
--  TÉCNICO — MANTENIMIENTO  (relación N:M)
-- ============================================================

CREATE TABLE tecnico_mantenimiento (
    id                   SERIAL PRIMARY KEY,
    id_mantenimiento_fk  INT    REFERENCES mantenimiento(id_mantenimiento) ON DELETE CASCADE,
    id_tecnico_fk        INT    REFERENCES perfil_tecnico(id_tecnico)      ON DELETE CASCADE,
    UNIQUE(id_mantenimiento_fk, id_tecnico_fk)
);


-- ============================================================
--  INCIDENCIAS
--  Ciclo de vida: pendiente → en_revision → resuelta → cerrada
-- ============================================================

CREATE TABLE incidencias (
    id_reporte               SERIAL              PRIMARY KEY,
    id_usuario_fk            INT                 REFERENCES usuarios(id_usuario)          ON DELETE SET NULL,
    id_espacio_fk            INT                 REFERENCES espacios(id_espacio)           ON DELETE SET NULL,
    id_equipo_fk             INT                 REFERENCES equipos(id_equipo)             ON DELETE SET NULL,
    fecha_generado           TIMESTAMP           DEFAULT CURRENT_TIMESTAMP,
    descripcion              TEXT                NOT NULL,

    -- Clasificación
    estado                   estado_incidencia   DEFAULT 'pendiente',
    prioridad                prioridad_incidencia DEFAULT 'media',

    -- Asignación a técnico
    id_tecnico_asignado_fk   INT                 REFERENCES perfil_tecnico(id_tecnico)     ON DELETE SET NULL,
    fecha_asignacion         TIMESTAMP,

    -- Resolución
    solucion                 TEXT,
    fecha_resolucion         TIMESTAMP,

    -- Mantenimiento generado a partir de esta incidencia (opcional)
    id_mantenimiento_fk      INT                 REFERENCES mantenimiento(id_mantenimiento) ON DELETE SET NULL
);


-- ============================================================
--  HISTORIAL DE AUDITORÍA
-- ============================================================

CREATE TABLE historial (
    id_historial      SERIAL          PRIMARY KEY,
    id_usuario_fk     INT             REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    accion            accion_auditoria NOT NULL,
    tabla_afectada    VARCHAR(100)     NOT NULL,
    registro_id       INT              NOT NULL,
    datos_anteriores  JSONB,
    datos_nuevos      JSONB,
    ip_address        INET,
    fecha             TIMESTAMP        DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
--  ÍNDICES
-- ============================================================

-- Historial
CREATE INDEX idx_historial_tabla   ON historial(tabla_afectada, registro_id);
CREATE INDEX idx_historial_usuario ON historial(id_usuario_fk);
CREATE INDEX idx_historial_fecha   ON historial(fecha);

-- Equipos / Usuarios
CREATE INDEX idx_equipo_codigo     ON equipos(codigo);
CREATE INDEX idx_usuario_correo    ON usuarios(correo);

-- Espacios
CREATE INDEX idx_espacio_pabellon  ON espacios(id_pabellon_fk);

-- Incidencias
CREATE INDEX idx_incidencia_fecha     ON incidencias(fecha_generado);
CREATE INDEX idx_incidencia_estado    ON incidencias(estado);
CREATE INDEX idx_incidencia_prioridad ON incidencias(prioridad);

-- Mantenimiento
CREATE INDEX idx_mantenimiento_estado ON mantenimiento(estado);


-- ============================================================
--  FUNCIÓN: updated_at automático
-- ============================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_usuario_updated_at
    BEFORE UPDATE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ============================================================
--  FUNCIÓN DE AUDITORÍA GENÉRICA
-- ============================================================

CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    v_usuario_id  INT;
    v_ip          INET;
    v_registro_id INT;
    v_pk_col      TEXT := TG_ARGV[0];
BEGIN
    v_usuario_id  := NULLIF(current_setting('app.current_user_id', TRUE), '')::INT;
    v_ip          := NULLIF(current_setting('app.ip_address',      TRUE), '')::INET;
    v_registro_id := (row_to_json(COALESCE(NEW, OLD)) ->> v_pk_col)::INT;

    INSERT INTO historial (
        id_usuario_fk, accion, tabla_afectada, registro_id,
        datos_anteriores, datos_nuevos, ip_address
    )
    VALUES (
        v_usuario_id,
        CASE TG_OP
            WHEN 'INSERT' THEN 'crear'
            WHEN 'UPDATE' THEN 'actualizar'
            WHEN 'DELETE' THEN 'eliminar'
        END::accion_auditoria,
        TG_TABLE_NAME,
        v_registro_id,
        CASE WHEN TG_OP = 'INSERT' THEN NULL ELSE row_to_json(OLD)::jsonb END,
        CASE WHEN TG_OP = 'DELETE' THEN NULL ELSE row_to_json(NEW)::jsonb END,
        v_ip
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;


-- ============================================================
--  TRIGGERS DE AUDITORÍA
-- ============================================================

CREATE TRIGGER trg_audit_pabellones
    AFTER INSERT OR UPDATE OR DELETE ON pabellones
    FOR EACH ROW EXECUTE FUNCTION audit_trigger('id_pabellon');

CREATE TRIGGER trg_audit_espacios
    AFTER INSERT OR UPDATE OR DELETE ON espacios
    FOR EACH ROW EXECUTE FUNCTION audit_trigger('id_espacio');

CREATE TRIGGER trg_audit_usuarios
    AFTER INSERT OR UPDATE OR DELETE ON usuarios
    FOR EACH ROW EXECUTE FUNCTION audit_trigger('id_usuario');

CREATE TRIGGER trg_audit_equipos
    AFTER INSERT OR UPDATE OR DELETE ON equipos
    FOR EACH ROW EXECUTE FUNCTION audit_trigger('id_equipo');

CREATE TRIGGER trg_audit_componentes
    AFTER INSERT OR UPDATE OR DELETE ON componentes
    FOR EACH ROW EXECUTE FUNCTION audit_trigger('id_componente');

CREATE TRIGGER trg_audit_productos_software
    AFTER INSERT OR UPDATE OR DELETE ON productos_software
    FOR EACH ROW EXECUTE FUNCTION audit_trigger('id_producto_software');

CREATE TRIGGER trg_audit_software_instalado
    AFTER INSERT OR UPDATE OR DELETE ON software_instalado
    FOR EACH ROW EXECUTE FUNCTION audit_trigger('id_instalacion');

CREATE TRIGGER trg_audit_mantenimiento
    AFTER INSERT OR UPDATE OR DELETE ON mantenimiento
    FOR EACH ROW EXECUTE FUNCTION audit_trigger('id_mantenimiento');

CREATE TRIGGER trg_audit_incidencias
    AFTER INSERT OR UPDATE OR DELETE ON incidencias
    FOR EACH ROW EXECUTE FUNCTION audit_trigger('id_reporte');