from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # Importação do Middleware CORS
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# --- INICIALIZAÇÃO DO FASTAPI ---
app = FastAPI(title="API de Recomendação de Filmes")

# --- BLOCO CORS CONFIGURADO AQUI ---
origins = [
    # Permite acesso do Live Server (porta 5500)
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    # Opcional: A própria API (porta 8000)
    "http://127.0.0.1:8000", 
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Lista de origens permitidas
    allow_credentials=True,        
    allow_methods=["*"],           # Permite todos os métodos
    allow_headers=["*"],           # Permite todos os cabeçalhos
)
# -----------------------------------

# Variáveis globais para armazenar os modelos e dados na memória
dados_globais = {
    "df_colaborativo": None,
    "sim_colaborativo": None,
    "df_conteudo": None,
    "sim_conteudo": None
}

def carregar_dados():
    """
    Função executada ao iniciar a API para carregar CSVs e treinar modelos.
    """
    print("Carregando dados... Isso pode levar alguns segundos.")
    
    # --- Carregando CSVs (Ajuste os caminhos conforme necessário) ---
    # Estou assumindo que estão na pasta 'data/'
    filmes = pd.read_csv('data/Filmes.csv', sep=',') # Ajuste o separador se necessário
    ratings = pd.read_csv('data/Ratings.csv', sep=';')
    dados_conteudo = pd.read_csv('data/Dados.csv')
    tags = pd.read_csv('data/Tags.csv')
    
    # ==========================================
    # 1. PREPARAÇÃO DO MÉTODO COLABORATIVO
    # ==========================================
    df_colab = filmes.merge(ratings, on='movieId')
    tabela_filmes = pd.pivot_table(df_colab, index='title', columns='userId', values='rating').fillna(0)
    
    # Calculando similaridade 
    rec_colab = cosine_similarity(tabela_filmes)
    rec_df_colab = pd.DataFrame(rec_colab, columns=tabela_filmes.index, index=tabela_filmes.index)
    
    dados_globais["sim_colaborativo"] = rec_df_colab

    # ==========================================
    # 2. PREPARAÇÃO DO MÉTODO CONTENT-BASED
    # ==========================================
    filmes['movieId'] = filmes['movieId'].astype(str)
    tags['movieId'] = tags['movieId'].astype(str)
    
    # Merges
    df2 = filmes.merge(dados_conteudo, left_on='title', right_on='Name', how='left')
    df2 = df2.merge(tags, left_on='movieId', right_on='movieId', how='left')
    
    # Tratamento de Nulos para evitar erro na concatenação
    df2 = df2.fillna('')
    
    # Criando a sopa de palavras (Feature Engineering)
    # Convertendo tudo para string para garantir
    df2['Infos'] = (
        df2['genres'] + " " + 
        df2['Directors_Cast'].astype(str) + " " + 
        df2['Discription'].astype(str) + " " + 
        df2['tag'].astype(str)
    )
    
    # Remove duplicatas de filmes para recomendação não repetir o mesmo filme
    df_conteudo_unico = df2.drop_duplicates(subset=['title']).reset_index(drop=True)
    
    vec = TfidfVectorizer(stop_words='english') # Adicionei stop_words para melhorar
    tfidf = vec.fit_transform(df_conteudo_unico['Infos'])
    
    sim_cont = cosine_similarity(tfidf)
    sim_df_cont = pd.DataFrame(sim_cont, columns=df_conteudo_unico['title'], index=df_conteudo_unico['title'])
    
    dados_globais["sim_conteudo"] = sim_df_cont
    print("Dados carregados com sucesso!")

# Evento de inicialização do FastAPI
@app.on_event("startup")
async def startup_event():
    carregar_dados()

# ==========================================
# ROTAS DA API
# ==========================================

@app.get("/")
def home():
    return {"mensagem": "API de Recomendação de Filmes Online!"}

@app.get("/recomendacao/colaborativa/{nome_filme}")
def recomendar_colaborativo(nome_filme: str):
    """
    Recomenda filmes baseado no gosto dos usuários (Ratings).
    """
    df_sim = dados_globais["sim_colaborativo"]
    
    if nome_filme not in df_sim.index:
        raise HTTPException(status_code=404, detail="Filme não encontrado na base colaborativa.")
    
    # Pega os 10 mais similares (excluindo o próprio filme)
    recomendacoes = df_sim[nome_filme].sort_values(ascending=False).iloc[1:11]
    
    return {
        "filme_origem": nome_filme,
        "metodo": "Colaborativo (User Ratings)",
        "recomendacoes": recomendacoes.to_dict()
    }

@app.get("/recomendacao/conteudo/{nome_filme}")
def recomendar_conteudo(nome_filme: str):
    """
    Recomenda filmes baseado nas características (Gênero, Diretor, Tags).
    """
    df_sim = dados_globais["sim_conteudo"]
    
    if nome_filme not in df_sim.index:
        raise HTTPException(status_code=404, detail="Filme não encontrado na base de conteúdo.")
    
    # Pega os 10 mais similares (excluindo o próprio filme)
    recomendacoes = df_sim[nome_filme].sort_values(ascending=False).iloc[1:11]
    
    return {
        "filme_origem": nome_filme,
        "metodo": "Content-Based (TF-IDF)",
        "recomendacoes": recomendacoes.to_dict()
    }