-- Archivo: resources_table.sql
-- Descripción: Script SQL para crear la tabla 'resources' en la base de datos de Neurocogniciones.
-- Esta tabla almacenará la información de los recursos que el bot ofrecerá a los estudiantes.

-- Crear la tabla 'resources' si no existe
CREATE TABLE IF NOT EXISTS resources (
    -- ID único para cada recurso. Es la clave primaria para identificar cada registro.
    resource_id SERIAL PRIMARY KEY,

    -- Nombre descriptivo del recurso. No puede ser nulo.
    resource_name VARCHAR(255) NOT NULL,

    -- Enlace (URL) donde se puede acceder al recurso. No puede ser nulo.
    link TEXT NOT NULL,

    -- Categoría principal del problema o área a la que pertenece el recurso (ej. 'aprendizaje', 'autogestión', 'autorregulación').
    -- Se basa en la categorización de problemas de los estudiantes mencionada en la reunión.
    category VARCHAR(100) NOT NULL,

    -- Subcategoría o problema específico dentro de la categoría (ej. 'olvido de estudio', 'falta de organización').
    -- Permite una clasificación más granular de los recursos.
    subcategory VARCHAR(100),

    -- Dificultad del recurso (ej. 'básico', 'avanzado').
    -- Esto permite al bot ofrecer recursos adaptados al nivel del estudiante.
    difficulty VARCHAR(50) NOT NULL,

    -- Marca de tiempo de cuándo se creó el registro del recurso.
    -- Útil para auditoría y seguimiento.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Marca de tiempo de la última actualización del registro del recurso.
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Crear un índice en la columna 'category' para optimizar las búsquedas por categoría.
CREATE INDEX IF NOT EXISTS idx_resources_category ON resources (category);

-- Crear un índice en la columna 'subcategory' para optimizar las búsquedas por subcategoría.
CREATE INDEX IF NOT EXISTS idx_resources_subcategory ON resources (subcategory);

-- Opcional: Insertar algunos datos de ejemplo para probar la tabla
-- Puedes eliminar o modificar estas líneas una vez que la base de datos esté en producción.
INSERT INTO resources (resource_name, link, category, subcategory, difficulty) VALUES
('Guia de Neurociencia Cognitiva', 'https://ejemplo.com/guia_neurociencia', 'aprendizaje', 'olvido de estudio', 'avanzado'),
('Tecnicas de Autogestion del Tiempo', 'https://ejemplo.com/tecnicas_tiempo', 'autogestion', 'falta de tiempo', 'basico'),
('Manejo de la Ansiedad para Estudiantes', 'https://ejemplo.com/ansiedad_estudio', 'autorregulacion', 'ansiedad', 'avanzado'),
('Estrategias para Superar la Desmotivacion', 'https://ejemplo.com/desmotivacion_estudio', 'autorregulacion', 'desmotivacion', 'basico'),
('Como Crear Esquemas Efectivos', 'https://ejemplo.com/esquemas_efectivos', 'aprendizaje', 'esquemas no adaptados', 'basico');

