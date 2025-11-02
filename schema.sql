-- Extensões necessárias para recursos de UUID e PostGIS
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS postgis;

-- Tabela existente para armazenar dados brutos de notícias
CREATE TABLE IF NOT EXISTS DadoBruto (
    id SERIAL PRIMARY KEY,
    fonte VARCHAR(255) NOT NULL,
    url_noticia TEXT UNIQUE,
    texto_completo TEXT NOT NULL,
    tipo_evento_classificado VARCHAR(255),
    locais_extraidos TEXT[],
    datas_extraidas TEXT[],
    data_coleta TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Usuários cadastrados na plataforma
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    face_reference VARCHAR(512) NOT NULL,
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_users_points_non_negative CHECK (points >= 0)
);

-- Configuração do modo guardião por usuário
CREATE TABLE IF NOT EXISTS guardian_modes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    active BOOLEAN DEFAULT FALSE,
    activated_at TIMESTAMP WITHOUT TIME ZONE,
    last_confirmation_at TIMESTAMP WITHOUT TIME ZONE,
    check_interval INTERVAL NOT NULL DEFAULT INTERVAL '6 hours',
    accessibility_permission BOOLEAN DEFAULT FALSE,
    lock_active BOOLEAN DEFAULT FALSE,
    CONSTRAINT ck_guardian_modes_check_interval_positive CHECK (check_interval > INTERVAL '0 hours')
);

-- Verificações periódicas do modo guardião
CREATE TABLE IF NOT EXISTS security_checks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guardian_mode_id UUID NOT NULL REFERENCES guardian_modes(id) ON DELETE CASCADE,
    requested_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    confirmed_at TIMESTAMP WITHOUT TIME ZONE,
    confirmed BOOLEAN DEFAULT FALSE
);

-- Eventos de bloqueio do modo guardião
CREATE TABLE IF NOT EXISTS lock_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    guardian_mode_id UUID NOT NULL REFERENCES guardian_modes(id) ON DELETE CASCADE,
    locked_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    unlocked_at TIMESTAMP WITHOUT TIME ZONE,
    reason VARCHAR(255)
);

-- Câmeras públicas cadastradas
CREATE TABLE IF NOT EXISTS cameras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_cameras_latitude_range CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_cameras_longitude_range CHECK (longitude BETWEEN -180 AND 180)
);

-- Pontos de iluminação cadastrados
CREATE TABLE IF NOT EXISTS lighting_spots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_lighting_latitude_range CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_lighting_longitude_range CHECK (longitude BETWEEN -180 AND 180)
);

-- Relatos enviados pela comunidade
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP WITHOUT TIME ZONE,
    is_valid BOOLEAN DEFAULT FALSE,
    points_awarded INTEGER DEFAULT 0,
    CONSTRAINT ck_reports_latitude_range CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_reports_longitude_range CHECK (longitude BETWEEN -180 AND 180),
    CONSTRAINT ck_reports_points_awarded_non_negative CHECK (points_awarded >= 0)
);

-- Medalhas para gamificação
CREATE TABLE IF NOT EXISTS badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    points_threshold INTEGER NOT NULL UNIQUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_badges_points_threshold_positive CHECK (points_threshold > 0)
);

-- Medalhas concedidas aos usuários
CREATE TABLE IF NOT EXISTS user_badges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    badge_id UUID NOT NULL REFERENCES badges(id) ON DELETE CASCADE,
    awarded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, badge_id)
);
