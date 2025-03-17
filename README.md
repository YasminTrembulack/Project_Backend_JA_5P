# Project_Backend_JA_5P
Backend project for the Learning Journey course in the 5th semester of Software Engineering in 2025.

## Ambiente virtual
Criando o ambiente: `python -m venv .venv`\
Ativando o ambiente: `.\.venv\Scripts\activate`\
Comando para desativar: `deactivate`

## Instalando pacotes
`pip install -r requirements.txt`

## Migrations LOCAL
> [!IMPORTANT]
> Caso uma migration já tenha sido iniciada apenas APLIQUE as migrações.\

Iniciar migrações: `alembic init migrations`\
Gerar migrações: `alembic revision --autogenerate -m "first migration"`\
Aplicar migrações: `alembic upgrade head`\
> Sempre que uma mudança relacionada ao banco de dados for realizada é necessario realizar as migrações.
