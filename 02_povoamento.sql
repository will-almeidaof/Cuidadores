-- ============================================================
-- SISTEMA DE REDE DE CUIDADORES E PACIENTES
-- Script 02: Povoamento do Banco de Dados
-- Disciplina: Fundamentos de Bancos de Dados 2026.1 - UFC
-- Autor: Willyam de Sousa Almeida
-- Obs: mínimo de 10 tuplas por tabela
-- ============================================================

-- ============================================================
-- USUÁRIOS (15 registros: 10 cuidadores + 5 administradores)
-- ============================================================
INSERT INTO usuario (nome, email, senha) VALUES
    ('Ana Lima',        'ana.lima@cuidar.com',       'hash_ana123'),
    ('Bruno Souza',     'bruno.souza@cuidar.com',    'hash_bru456'),
    ('Carla Mendes',    'carla.mendes@cuidar.com',   'hash_car789'),
    ('Diego Ferreira',  'diego.ferreira@cuidar.com', 'hash_die012'),
    ('Elaine Costa',    'elaine.costa@cuidar.com',   'hash_ela345'),
    ('Felipe Rocha',    'felipe.rocha@cuidar.com',   'hash_fel678'),
    ('Gabriela Nunes',  'gabriela.nunes@cuidar.com', 'hash_gab901'),
    ('Henrique Alves',  'henrique.alves@cuidar.com', 'hash_hen234'),
    ('Isabela Martins', 'isabela.martins@cuidar.com','hash_isa567'),
    ('Jonas Pereira',   'jonas.pereira@cuidar.com',  'hash_jon890'),
    ('Karla Vieira',    'karla.vieira@cuidar.com',   'hash_kar111'),
    ('Lucas Oliveira',  'lucas.oliveira@cuidar.com', 'hash_luc222'),
    ('Marina Batista',  'marina.batista@cuidar.com', 'hash_mar333'),
    ('Nelson Gomes',    'nelson.gomes@cuidar.com',   'hash_nel444'),
    ('Olivia Teixeira', 'olivia.teixeira@cuidar.com','hash_oli555');

-- ============================================================
-- CUIDADORES (ids 1 a 10 → usuários 1–10)
-- ============================================================
INSERT INTO cuidador (id_usuario, cpf) VALUES
    (1,  '11122233301'),
    (2,  '22233344402'),
    (3,  '33344455503'),
    (4,  '44455566604'),
    (5,  '55566677705'),
    (6,  '66677788806'),
    (7,  '77788899907'),
    (8,  '88899900008'),
    (9,  '99900011109'),
    (10, '10011122210');

-- ============================================================
-- ADMINISTRADORES (ids 11 a 15)
-- ============================================================
INSERT INTO administrador (id_usuario) VALUES
    (11),
    (12),
    (13),
    (14),
    (15);

-- ============================================================
-- TELEFONES DE CUIDADORES (atributo multivalorado — 15 registros)
-- ============================================================
INSERT INTO telefone_cuidador (id_usuario, telefone) VALUES
    (1,  '(85) 98001-1001'),
    (1,  '(85) 98001-1002'),  -- cuidador 1 tem dois telefones
    (2,  '(85) 98002-2002'),
    (3,  '(85) 98003-3003'),
    (4,  '(85) 98004-4004'),
    (5,  '(85) 98005-5005'),
    (6,  '(85) 98006-6006'),
    (7,  '(85) 98007-7007'),
    (7,  '(85) 98007-7008'),  -- cuidador 7 tem dois telefones
    (8,  '(85) 98008-8008'),
    (9,  '(85) 98009-9009'),
    (10, '(85) 98010-0010'),
    (3,  '(85) 98003-3030'),  -- cuidador 3 tem dois telefones
    (5,  '(85) 98005-5050'),
    (9,  '(85) 98009-9090');

-- ============================================================
-- PACIENTES (12 registros)
-- ============================================================
INSERT INTO paciente (nome, data_nascimento) VALUES
    ('Maria das Graças',  '1942-03-15'),
    ('José Antônio',      '1938-07-22'),
    ('Raimunda Sousa',    '1950-11-05'),
    ('Francisco Barros',  '1945-01-30'),
    ('Conceição Lopes',   '1933-09-18'),
    ('Manoel Rodrigues',  '1948-06-12'),
    ('Benedita Carvalho', '1955-04-25'),
    ('Antônio Ferreira',  '1940-12-08'),
    ('Luzia Nascimento',  '1952-02-14'),
    ('Sebastião Lima',    '1936-08-03'),
    ('Terezinha Alves',   '1944-05-20'),
    ('Raimundo Costa',    '1939-10-17');

-- ============================================================
-- HISTÓRICO MÉDICO (atributo multivalorado — 15 registros)
-- ============================================================
INSERT INTO historico_medico (id_paciente, descricao, data_registro) VALUES
    (1,  'Diagnóstico de hipertensão arterial',              '2020-03-10'),
    (1,  'Inicio de tratamento para diabetes tipo 2',        '2021-06-15'),
    (2,  'Histórico de AVC isquêmico em 2018',              '2019-01-20'),
    (2,  'Uso contínuo de anticoagulantes',                  '2019-02-05'),
    (3,  'Osteoporose diagnosticada',                        '2017-08-22'),
    (4,  'Insuficiência cardíaca compensada',                '2022-04-11'),
    (5,  'Doença de Alzheimer fase inicial',                 '2023-01-30'),
    (6,  'Diabetes tipo 2 controlado com insulina',          '2018-09-14'),
    (7,  'Parkinson diagnosticado — uso de levodopa',        '2021-11-05'),
    (8,  'Histórico de infarto agudo do miocárdio',          '2015-07-19'),
    (9,  'Artrite reumatoide com comprometimento funcional', '2019-03-28'),
    (10, 'DPOC — doença pulmonar obstrutiva crônica',        '2020-12-01'),
    (11, 'Hipotireoidismo em tratamento',                    '2016-05-17'),
    (12, 'Insuficiência renal crônica estágio 3',            '2022-09-09'),
    (5,  'Episódio de desorientação noturna registrado',     '2023-08-12');

-- ============================================================
-- CUIDA — associação cuidador ↔ paciente (12 registros)
-- ============================================================
INSERT INTO cuida (id_cuidador, id_paciente, data_inicio, data_fim) VALUES
    (1,  1,  '2023-01-10', NULL),
    (1,  2,  '2023-03-01', '2024-02-28'),
    (2,  3,  '2022-07-15', NULL),
    (3,  4,  '2023-05-20', NULL),
    (4,  5,  '2024-01-05', NULL),
    (5,  6,  '2022-11-01', '2023-11-01'),
    (6,  7,  '2023-08-10', NULL),
    (7,  8,  '2021-06-01', NULL),
    (8,  9,  '2023-02-14', NULL),
    (9,  10, '2022-04-22', NULL),
    (10, 11, '2024-03-01', NULL),
    (2,  12, '2023-09-18', NULL);

-- ============================================================
-- ATIVIDADES (12 registros)
-- ============================================================
INSERT INTO atividade (descricao, data_hora, tipo, id_cuidador, id_paciente) VALUES
    ('Administração de medicamento anti-hipertensivo',  '2024-06-01 08:00:00', 'Medicação',       1, 1),
    ('Auxílio no banho e higiene pessoal',              '2024-06-01 09:30:00', 'Higiene',         1, 1),
    ('Exercícios de fisioterapia domiciliar',           '2024-06-02 10:00:00', 'Fisioterapia',    2, 3),
    ('Verificação de pressão arterial e glicemia',      '2024-06-02 07:45:00', 'Monitoramento',   3, 4),
    ('Preparo e oferta de refeição balanceada',         '2024-06-03 12:00:00', 'Alimentação',     4, 5),
    ('Acompanhamento em consulta médica',               '2024-06-04 14:00:00', 'Acompanhamento',  5, 6),
    ('Troca de curativo em membro inferior',            '2024-06-05 09:00:00', 'Curativo',        6, 7),
    ('Estimulação cognitiva com atividades lúdicas',    '2024-06-05 15:00:00', 'Estimulação',     7, 8),
    ('Administração de insulina',                       '2024-06-06 07:30:00', 'Medicação',       8, 9),
    ('Auxílio na mobilidade e prevenção de quedas',     '2024-06-06 11:00:00', 'Mobilidade',      9, 10),
    ('Leitura e acompanhamento recreativo',             '2024-06-07 16:00:00', 'Recreação',       10, 11),
    ('Monitoramento de saturação de oxigênio',          '2024-06-07 08:30:00', 'Monitoramento',   2, 12);

-- ============================================================
-- OCORRÊNCIAS (12 registros)
-- ============================================================
INSERT INTO ocorrencia (descricao, data_hora, gravidade, id_cuidador, id_paciente) VALUES
    ('Paciente apresentou pico hipertensivo — PA 180x110',   '2024-06-01 10:15:00', 'alta',  1, 1),
    ('Queda no banheiro sem lesões aparentes',               '2024-06-02 08:00:00', 'media', 2, 3),
    ('Paciente recusou medicação por duas doses consecutivas','2024-06-02 12:30:00', 'baixa', 3, 4),
    ('Episódio de confusão mental e desorientação',          '2024-06-03 22:00:00', 'alta',  4, 5),
    ('Vômito após refeição — possível intolerância',         '2024-06-03 13:00:00', 'media', 5, 6),
    ('Edema em membros inferiores observado',                '2024-06-04 09:30:00', 'media', 6, 7),
    ('Paciente relatou dor torácica leve — SAMU acionado',  '2024-06-05 03:00:00', 'alta',  7, 8),
    ('Glicemia abaixo de 70 mg/dL — hipoglicemia leve',     '2024-06-05 07:00:00', 'media', 8, 9),
    ('Dificuldade respiratória — uso de broncodilatador',   '2024-06-06 14:00:00', 'alta',  9, 10),
    ('Paciente agitado durante a noite — insônia relatada', '2024-06-06 23:00:00', 'baixa', 10, 11),
    ('Febre de 38.5°C detectada — médico notificado',       '2024-06-07 16:30:00', 'media', 2, 12),
    ('Paciente reclamou de tontura ao levantar',             '2024-06-07 10:00:00', 'baixa', 1, 1);
