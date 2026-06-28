# Sistema de Rede de Cuidadores e Pacientes
**Fundamentos de Bancos de Dados 2026.1 — UFC**  
Autor: Willyam de Sousa Almeida

---

## Estrutura do projeto

```
├── 01_criacao.sql      # Criação das tabelas
├── 02_povoamento.sql   # Inserção de dados
├── db.py               # Models SQLAlchemy + configuração de conexão
├── app.ipynb           # Protótipo de aplicação (Panel + Jupyter)
└── README.md
```

## Requisitos

- Python 3.9+
- PostgreSQL rodando localmente

## Instalação

```bash
pip install panel psycopg2-binary sqlalchemy pandas jupyter
```

## Configuração do banco

1. Crie o banco no PostgreSQL:
```sql
CREATE DATABASE cuidadores_db;
```

2. Execute os scripts na ordem:
```bash
psql -U postgres -d cuidadores_db -f 01_criacao.sql
psql -U postgres -d cuidadores_db -f 02_povoamento.sql
```

3. Ajuste as credenciais em `db.py` (variáveis `DB_USER`, `DB_PASSWORD`, etc.) se necessário.

## Executando o protótipo

```bash
jupyter notebook app.ipynb
```

Execute as células em ordem. A última célula renderiza a aplicação com abas interativas.

Para servir como app standalone:
```bash
panel serve app.ipynb --show
```

## Telas implementadas

| Tela | Entidade principal | Operações |
|---|---|---|
| 👤 Pacientes | `paciente` | Inserir, Listar, Editar, Remover |
| 🩺 Cuidadores | `usuario` + `cuidador` + `telefone_cuidador` | Inserir, Listar, Editar, Remover |
| 📋 Atividades | `atividade` | Inserir, Listar, Editar, Remover |
| 🚨 Ocorrências | `ocorrencia` | Inserir, Listar, Editar, Remover |
