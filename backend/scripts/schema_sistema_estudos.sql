-- Schema de referência (pode rodar no MySQL OU deixar o Django criar via `migrate`).
-- Se criar manualmente, depois: `python manage.py migrate --fake-initial`

CREATE DATABASE IF NOT EXISTS sistema_estudos;
USE sistema_estudos;

CREATE TABLE aluno (
    id_aluno INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL
);

CREATE TABLE disciplina (
    id_disciplina INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id_aluno INT,
    nome VARCHAR(100),
    nivel_dificuldade INT,
    data_exclusao DATETIME,
    FOREIGN KEY (aluno_id_aluno) REFERENCES aluno(id_aluno)
);

CREATE TABLE tarefa (
    id_tarefa INT AUTO_INCREMENT PRIMARY KEY,
    disciplina_id_disciplina INT,
    descricao VARCHAR(255),
    data_entrega DATE,
    status_tarefa VARCHAR(20),
    data_exclusao DATETIME,
    FOREIGN KEY (disciplina_id_disciplina) REFERENCES disciplina(id_disciplina)
);

CREATE TABLE sessao_estudo (
    id_sessao_estudo INT AUTO_INCREMENT PRIMARY KEY,
    disciplina_id_disciplina INT,
    aluno_id_aluno INT,
    tempo_estudo DECIMAL(5,2),
    data_sessao DATE,
    nivel_dificuldade INT,
    data_exclusao DATETIME,
    FOREIGN KEY (disciplina_id_disciplina) REFERENCES disciplina(id_disciplina),
    FOREIGN KEY (aluno_id_aluno) REFERENCES aluno(id_aluno)
);

CREATE TABLE relatorio (
    id_relatorio INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id_aluno INT,
    periodo VARCHAR(50),
    total_horas DECIMAL(5,2),
    data_exclusao DATETIME,
    FOREIGN KEY (aluno_id_aluno) REFERENCES aluno(id_aluno)
);

CREATE TABLE sugestao (
    id_sugestao INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id_aluno INT,
    descricao VARCHAR(255),
    data_exclusao DATETIME,
    FOREIGN KEY (aluno_id_aluno) REFERENCES aluno(id_aluno)
);

CREATE TABLE log_atividade (
    id_log_atividade INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id_aluno INT,
    acao VARCHAR(150),
    tabela_afetada VARCHAR(150),
    id_registro_afetado INT,
    descricao VARCHAR(255),
    data_hora DATETIME,
    FOREIGN KEY (aluno_id_aluno) REFERENCES aluno(id_aluno)
);
