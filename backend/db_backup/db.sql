CREATE TABLE encuestas (
    marca_temporal VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    correo_electronico VARCHAR(255) NOT NULL UNIQUE,
    edad VARCHAR(255) NOT NULL,
    genero VARCHAR(255) NOT NULL,
    nombre_banco VARCHAR(255) NOT NULL,
    calidad_servicio VARCHAR(255) NOT NULL,
    satisfaccion_personal VARCHAR(255) NOT NULL,
    personal_capacitado VARCHAR(255) NOT NULL,
    frecuencia_uso VARCHAR(255) NOT NULL,
    facilidad_canales_digitales VARCHAR(255) NOT NULL,
    rapidez_respuesta VARCHAR(255) NOT NULL,
    resolucion_primer_contacto VARCHAR(255) NOT NULL,
    cambiar_banco VARCHAR(255) NOT NULL,
    relacion_costo_beneficio VARCHAR(255) NOT NULL,
    accesibilidad_personal VARCHAR(255) NOT NULL,
    preferencia_atencion VARCHAR(255) NOT NULL,
    comparacion_otros_bancos VARCHAR(255) NOT NULL,
    vanguardia_tecnologia VARCHAR(255) NOT NULL,
    seguridad_servicios VARCHAR(255) NOT NULL,
    recomendaria_banco VARCHAR(255) NOT NULL
);

ALTER TABLE encuestas
ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST;
