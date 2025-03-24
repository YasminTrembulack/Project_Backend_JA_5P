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

## Tasks
Para rodar o comando basta colocar task a seguir o comando. Exemplo `task run`.
* **lint:** Verifica a qualidade do código usando o Ruff, analisando erros de estilo e boas práticas.
* **pre_format:** Corrige automaticamente os problemas detectados pelo Ruff antes de formatar o código.
* **format:** Formata o código seguindo as regras definidas pelo Ruff.
* **run:** Inicia a aplicação FastAPI com o Uvicorn, tornando-a acessível em `http://0.0.0.0:8000`.
* **pre_test:** Garante que o código passou pelo processo de linting antes de rodar os testes.
* **test:** Executa os testes com Pytest, medindo a cobertura de código e exibindo detalhes extras.
* **post_test:** Gera um relatório em HTML com a cobertura de código após a execução dos testes.