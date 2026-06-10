🎬 Sistema de Recomendação de Filmes

Visão Geral

Este projeto implementa uma API de recomendação de filmes robusta e de alto desempenho, utilizando o framework FastAPI em Python. O sistema combina duas das abordagens mais poderosas em Machine Learning para oferecer sugestões personalizadas: a Recomendação Colaborativa (baseada no comportamento de outros usuários) e a Recomendação Baseada em Conteúdo (baseada nas características do filme).

O front-end é uma interface simples, moderna e responsiva desenvolvida em HTML/CSS (Tailwind CSS) e JavaScript, utilizada para interagir em tempo real com os endpoints da API.

⚙️ Tecnologias Utilizadas

Componente

Tecnologia

Descrição

Backend (API)

Python 3.x

Linguagem de programação principal.

Framework Web

FastAPI

Framework moderno e rápido para construir APIs.

Cálculo ML

Scikit-learn

Utilizado para calcular a Similaridade de Cosseno.

Manipulação de Dados

Pandas / NumPy

Essencial para processamento, pivotamento e limpeza de datasets.

Servidor

Uvicorn

Servidor ASGI de alta performance para rodar o FastAPI.

Frontend

HTML5, JavaScript

Interface para consumo da API.

Estilização

Tailwind CSS

Framework CSS utilitário para design rápido e responsivo.

🏗️ Arquitetura do Sistema

A arquitetura do projeto segue um modelo de microserviço simples:

Pré-carga e Modelos (main.py): Ao iniciar, a API carrega os quatro datasets (Filmes.csv, Ratings.csv, Dados.csv, Tags.csv) e pré-calcula as duas matrizes de similaridade (Colaborativa e Content-Based). Isso garante que as requisições subsequentes sejam respondidas em milissegundos.

Endpoints (main.py): O FastAPI expõe rotas GET para cada método de recomendação.

Frontend (index.html): O JavaScript utiliza a função fetch() para enviar o nome do filme para a API e renderiza a lista de resultados.

CORS: O middleware CORS foi configurado no FastAPI para permitir a comunicação segura entre o Live Server (porta 5500) e a API (porta 8000).

🚀 Setup e Execução do Projeto

Siga os passos abaixo para colocar o sistema em funcionamento no seu ambiente local (recomendado VS Code e PowerShell).

1. Estrutura de Diretórios

Organize o projeto com a seguinte estrutura e adicione seus arquivos .csv na pasta data/:

A3 montanha/
├── data/
│   ├── Filmes.csv
│   ├── Ratings.csv
│   ├── Dados.csv
│   └── Tags.csv
├── main.py
├── index.html
└── requeriments.txt


2. Configuração do Ambiente Virtual

É crucial utilizar um ambiente virtual (.venv) para isolar as dependências do projeto.

Crie o Ambiente Virtual (se ainda não existir):

python -m venv .venv


Ative o Ambiente Virtual:

& .\.venv\Scripts\Activate.ps1


Confirme que o prompt do terminal mostra (.venv) no início.

3. Instalação das Dependências

Instale todas as bibliotecas listadas no requeriments.txt:

pip install -r requeriments.txt


4. Iniciar a API (Backend)

Com o ambiente virtual ativo, execute o servidor Uvicorn:

uvicorn main:app --reload


A API será inicializada na porta http://127.0.0.1:8000. Você verá a mensagem "Dados carregados com sucesso!" no console.

5. Iniciar o Frontend

Abra o arquivo index.html no VS Code.

Clique com o botão direito e selecione "Open with Live Server" (ou abra o arquivo diretamente no navegador). O Live Server geralmente utiliza a porta 5500.

🌐 Endpoints da API

A API expõe dois endpoints principais para recomendação, acessíveis em http://127.0.0.1:8000:

Método

Rota

Descrição

GET

/recomendacao/colaborativa/{nome_filme}

Usa a matriz de similaridade entre usuários (Ratings) para sugerir 10 filmes.

GET

/recomendacao/conteudo/{nome_filme}

Usa a similaridade TF-IDF (Gêneros, Diretores, Tags) para sugerir 10 filmes.

Exemplo de Uso (CURL)

# Exemplo de requisição Content-Based via terminal:
curl -X 'GET' \
  '[http://127.0.0.1:8000/recomendacao/conteudo/Toy%20Story](http://127.0.0.1:8000/recomendacao/conteudo/Toy%20Story)' \
  -H 'accept: application/json'


⚠️ Solução de Problemas Comuns

Problema

Mensagem de Erro

Solução

uvicorn não reconhecido

"O termo 'uvicorn' não é reconhecido..."

Ative o ambiente virtual usando & .\.venv\Scripts\Activate.ps1 antes de rodar o comando uvicorn.

Erro no Frontend

"Failed to fetch" (Erro ao buscar)

Verifique: 1) Se a API está rodando na porta 8000. 2) Se o CORS está configurado corretamente no main.py para aceitar a origem http://127.0.0.1:5500.

Erro de Sintaxe

SyntaxError: invalid syntax na linha 9

Remova a linha de comando uvicorn main:app --reload do seu arquivo main.py. Este é um comando de terminal, não código Python.
