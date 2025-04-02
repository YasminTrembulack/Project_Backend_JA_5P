# Project_Backend_JA_5P [![Coverage Status](https://coveralls.io/repos/github/YasminTrembulack/Project_Backend_JA_5P/badge.svg)](https://coveralls.io/github/YasminTrembulack/Project_Backend_JA_5P)
Backend project for the Learning Journey course in the 5th semester of Software Engineering in 2025.\
## Tecnologias Utilizadas
- **Backend:** Python, FastAPI
- **Banco de Dados:** MySQL
- **Outras tecnologias relevantes:** SQLAlchemy, Alembic, PyMySQL, pydantic, ruff, loguru, etc.

## Requisitos
Antes de rodar o projeto, você precisa instalar o MySQL no seu ambiente local.

### Instalar MySQL
1.  Clique no link abaixo para acessar um tutorial de instalação do MySQL: [Tutorial de Instalação do MySQL](https://www.youtube.com/watch?v=v8i2NgiM5pE)
2.  Siga as instruções do tutorial para instalar o MySQL no seu sistema.
3.  Após a instalação, verifique se o MySQL está funcionando corretamente executando o seguinte comando no terminal: `mysql --version`


### Configurando ambiente virtual
1.  Criando o ambiente: `python -m venv .venv`\
2.  Ativando o ambiente: `.\.venv\Scripts\activate`\
3.  Comando para desativar: `deactivate`
4.  Instalando pacotes: `pip install -r requirements.txt`

### Migrations Local
> [!IMPORTANT]
> Caso uma migration já tenha sido iniciada apenas APLIQUE as migrações.

1.  Iniciar migrações: `alembic init migrations`
2.  Gerar migrações: `alembic revision --autogenerate -m "first migration"`
3.  Aplicar migrações: `alembic upgrade head`

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


# TODO: criar um metodo dentro de mold service, que quando chamado atualize as prioridades dos moldes, alem disso adicionar um atributo em parts que seja a porcetagem de conclusao da peça, facilitando na hora da conta, apos isso atualizar os metodos que calcular a prioridade ou a conclusao em %
