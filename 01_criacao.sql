-- ============================================================
-- SISTEMA DE REDE DE CUIDADORES E PACIENTES
-- Script 01: Criação do Modelo Relacional
-- Disciplina: Fundamentos de Bancos de Dados 2026.1 - UFC
-- Autor: Willyam de Sousa Almeida
-- ============================================================

-- Limpa o schema se necessário (ordem inversa de dependência)
DROP TABLE IF EXISTS ocorrencia       CASCADE;
DROP TABLE IF EXISTS atividade        CASCADE;
DROP TABLE IF EXISTS cuida            CASCADE;
DROP TABLE IF EXISTS historico_medico CASCADE;
DROP TABLE IF EXISTS paciente         CASCADE;
DROP TABLE IF EXISTS telefone_cuidador CASCADE;
DROP TABLE IF EXISTS cuidador         CASCADE;
DROP TABLE IF EXISTS administrador    CASCADE;
DROP TABLE IF EXISTS usuario          CASCADE;
DROP TYPE  IF EXISTS gravidade_enum;

-- ============================================================
-- TABELA: usuario (superclasse)
-- ============================================================
CREATE TABLE usuario (
    id_usuario SERIAL        PRIMARY KEY,
    nome       VARCHAR(100)  NOT NULL,
    email      VARCHAR(150)  NOT NULL UNIQUE,
    senha      VARCHAR(255)  NOT NULL
);

-- ============================================================
-- TABELA: cuidador (subclasse de usuario — especialização total disjunta)
-- ============================================================
CREATE TABLE cuidador (
    id_usuario INTEGER     PRIMARY KEY REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    cpf        CHAR(11)    NOT NULL UNIQUE
);

-- ============================================================
-- TABELA: administrador (subclasse de usuario — especialização total disjunta)
-- ============================================================
CREATE TABLE administrador (
    id_usuario INTEGER PRIMARY KEY REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

-- ============================================================
-- TABELA: telefone_cuidador (atributo multivalorado de cuidador)
-- ============================================================
CREATE TABLE telefone_cuidador (
    id         SERIAL      PRIMARY KEY,
    id_usuario INTEGER     NOT NULL REFERENCES cuidador(id_usuario) ON DELETE CASCADE,
    telefone   VARCHAR(20) NOT NULL
);

-- ============================================================
-- TABELA: paciente
-- ============================================================
CREATE TABLE paciente (
    id_paciente      SERIAL       PRIMARY KEY,
    nome             VARCHAR(100) NOT NULL,
    data_nascimento  DATE         NOT NULL
);

-- ============================================================
-- TABELA: historico_medico (atributo multivalorado de paciente)
-- ============================================================
CREATE TABLE historico_medico (
    id          SERIAL        PRIMARY KEY,
    id_paciente INTEGER       NOT NULL REFERENCES paciente(id_paciente) ON DELETE CASCADE,
    descricao   TEXT          NOT NULL,
    data_registro DATE        NOT NULL DEFAULT CURRENT_DATE
);

-- ============================================================
-- TABELA: cuida (relacionamento N:N entre cuidador e paciente)
-- ============================================================
CREATE TABLE cuida (
    id_cuidador  INTEGER NOT NULL REFERENCES cuidador(id_usuario) ON DELETE CASCADE,
    id_paciente  INTEGER NOT NULL REFERENCES paciente(id_paciente) ON DELETE CASCADE,
    data_inicio  DATE    NOT NULL,
    data_fim     DATE,
    PRIMARY KEY (id_cuidador, id_paciente, data_inicio)
);

-- ============================================================
-- TIPO ENUM: gravidade para ocorrencias
-- ============================================================
CREATE TYPE gravidade_enum AS ENUM ('baixa', 'media', 'alta');

-- ============================================================
-- TABELA: atividade
-- ============================================================
CREATE TABLE atividade (
    id_atividade SERIAL          PRIMARY KEY,
    descricao    TEXT            NOT NULL,
    data_hora    TIMESTAMP       NOT NULL,
    tipo         VARCHAR(80)     NOT NULL,
    id_cuidador  INTEGER         NOT NULL REFERENCES cuidador(id_usuario),
    id_paciente  INTEGER         NOT NULL REFERENCES paciente(id_paciente)
);

-- ============================================================
-- TABELA: ocorrencia
-- ============================================================
CREATE TABLE ocorrencia (
    id_ocorrencia SERIAL          PRIMARY KEY,
    descricao     TEXT            NOT NULL,
    data_hora     TIMESTAMP       NOT NULL,
    gravidade     gravidade_enum  NOT NULL,
    id_cuidador   INTEGER         NOT NULL REFERENCES cuidador(id_usuario),
    id_paciente   INTEGER         NOT NULL REFERENCES paciente(id_paciente)
);
