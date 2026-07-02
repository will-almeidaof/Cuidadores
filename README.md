# Sistema de Rede de Cuidadores e Pacientes

Aplicação web para gerenciamento de uma rede de cuidadores e pacientes, desenvolvida como projeto da disciplina **Fundamentos de Bancos de Dados 2026.1 — UFC**.

O sistema permite cadastrar pacientes e cuidadores, vincular cuidadores a pacientes, e registrar atividades e ocorrências durante o atendimento, com um dashboard e telas de CRUD completo (criar, listar, editar e remover) para cada entidade.

**Autor:** Willyam de Sousa Almeida

---

## Stack utilizada

- **Backend:** Python 3 + Flask
- **Acesso a dados:** SQLAlchemy (ORM) e psycopg2 (driver PostgreSQL)
- **Banco de dados:** PostgreSQL
- **Frontend:** HTML, CSS e JavaScript puro (SPA de página única, consumindo a API via `fetch`)

---

## Estrutura do projeto

```
.
├── app_flask.py               # Backend: models SQLAlchemy + rotas da API REST
├── templates/
│   └── index.html             # Frontend: dashboard e telas de CRUD
├── 01_criacao.sql             # Script de criação do schema (DDL)
├── 02_povoamento.sql          # Script de povoamento (mínimo 10 tuplas por tabela)
├── esquema_relacional.png     # Diagrama do modelo relacional
└── eer_conceitual.png         # Diagrama do modelo conceitual (EER)
```

> **Observação:** o Flask serve `index.html` via `render_template`, então o arquivo precisa estar dentro de uma pasta `templates/` no mesmo diretório de `app_flask.py`.

---

## Modelo de dados

O banco é composto pelas tabelas:

| Tabela | Descrição |
|---|---|
| `usuario` | Superclasse de `cuidador` e `administrador` (especialização total e disjunta) |
| `cuidador` | Subclasse de `usuario`; possui CPF único |
| `administrador` | Subclasse de `usuario` |
| `telefone_cuidador` | Atributo multivalorado — telefones de um cuidador |
| `paciente` | Dados do paciente (nome, data de nascimento) |
| `historico_medico` | Atributo multivalorado — histórico clínico de um paciente |
| `cuida` | Relacionamento N:N entre `cuidador` e `paciente`, com `data_inicio`/`data_fim` |
| `atividade` | Atividades realizadas por um cuidador em um paciente |
| `ocorrencia` | Ocorrências (com `gravidade`: baixa / media / alta) registradas durante o atendimento |

Os diagramas completos estão em `esquema_relacional.png` (modelo relacional) e `eer_conceitual.png` (modelo EER).

---

## Pré-requisitos

- Python 3.10+
- PostgreSQL instalado e em execução
- `pip`

---

## Instalação

1. **Clone o repositório e entre na pasta do projeto**

   ```bash
   git clone <url-do-repositorio>
   cd <pasta-do-projeto>
   ```

2. **Crie um ambiente virtual (recomendado)**

   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/Mac
   venv\Scripts\activate         # Windows
   ```

3. **Instale as dependências**

   ```bash
   pip install flask flask_sqlalchemy psycopg2-binary
   ```

4. **Crie o banco de dados no PostgreSQL**

   ```bash
   createdb cuidadores_db
   ```

   ou, via `psql`:

   ```sql
   CREATE DATABASE cuidadores_db;
   ```

5. **Execute os scripts SQL para criar e popular as tabelas**

   ```bash
   psql -U postgres -d cuidadores_db -f 01_criacao.sql
   psql -U postgres -d cuidadores_db -f 02_povoamento.sql
   ```

6. **Configure a conexão com o banco**

   Em `app_flask.py`, ajuste as credenciais se necessário:

   ```python
   DB_USER     = "postgres"
   DB_PASSWORD = "1234"
   DB_HOST     = "localhost"
   DB_PORT     = "5432"
   DB_NAME     = "cuidadores_db"
   ```

7. **Coloque o `index.html` dentro de uma pasta `templates/`**

   ```bash
   mkdir -p templates
   mv index.html templates/
   ```

8. **Rode a aplicação**

   ```bash
   python app_flask.py
   ```

9. **Acesse no navegador**

   ```
   http://localhost:5000
   ```

---

## Funcionalidades

O frontend possui um dashboard com contadores gerais e telas de CRUD para:

- **Pacientes** — cadastro, edição, remoção e listagem, com busca por nome
- **Cuidadores** — cadastro, edição, remoção e listagem, com telefones multivalorados e busca
- **Vínculos (cuida)** — associação entre cuidador e paciente, com data de início/fim e validação contra vínculos ativos duplicados
- **Atividades** — registro de atividades realizadas, com filtros por tipo, paciente e período
- **Ocorrências** — registro de ocorrências com nível de gravidade (baixa/media/alta), com filtros por paciente, gravidade e período

Remoções que afetam registros dependentes (atividades/ocorrências vinculadas) pedem confirmação antes de excluir em cascata.

---

## API REST

Todas as rotas retornam JSON no formato `{ "ok": true/false, "data": ... }`.

| Recurso | Rotas |
|---|---|
| Pacientes | `GET /api/pacientes` · `POST /api/pacientes` · `PUT /api/pacientes/<id>` · `DELETE /api/pacientes/<id>` |
| Cuidadores | `GET /api/cuidadores` · `POST /api/cuidadores` · `PUT /api/cuidadores/<id>` · `DELETE /api/cuidadores/<id>` |
| Vínculos | `GET /api/vinculos` · `POST /api/vinculos` · `PUT /api/vinculos/<id>` · `DELETE /api/vinculos/<id>` |
| Atividades | `GET /api/atividades` · `POST /api/atividades` · `PUT /api/atividades/<id>` · `DELETE /api/atividades/<id>` |
| Ocorrências | `GET /api/ocorrencias` · `POST /api/ocorrencias` · `PUT /api/ocorrencias/<id>` · `DELETE /api/ocorrencias/<id>` |

---

## Referência

ELMASRI, R.; NAVATHE, S. B. **Sistemas de Banco de Dados**. 6ª Edição, Pearson Brasil, 2011.
