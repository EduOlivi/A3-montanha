from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import create_engine
import os

# --- INICIALIZAÇÃO DO FASTAPI ---
app = FastAPI(title="API de Recomendação de Filmes")

# --- BLOCO CORS CONFIGURADO ---
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000", 
    "http://localhost:8000",
    "*" # Permite que o seu front-end na Vercel ou qualquer outra origem aceda à API
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,        
    allow_methods=["*"],           
    allow_headers=["*"],           
)
# -----------------------------------

# --- CONEXÃO COM O BANCO DE DADOS RELACIONAL ---
DATABASE_URL = "postgresql://filmes_o78y_user:8Dn3409RciyqTob6w5tndAJPkyc6jBLp@dpg-d8ktig647okc73b7uq20-a.virginia-postgres.render.com/filmes_o78y"

# Ajuste obrigatório exigido pelo SQLAlchemy para links do Render
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
# -----------------------------------------------

# Variáveis globais para armazenar os modelos e dados na memória
dados_globais = {
    "sim_colaborativo": None,
    "sim_conteudo": None
}

def carregar_dados():
    """
    Função executada ao iniciar a API para ler do PostgreSQL na nuvem e treinar modelos.
    """
    print("🔌 Conectando ao banco de dados e carregando dados... Isso pode levar alguns segundos.")
    
    try:
        # =========================================================
        # 1. CARREGAMENTO DOS DADOS VIA SQL
        # =========================================================
        filmes = pd.read_sql("SELECT * FROM filmes", engine)
        dados_conteudo = pd.read_sql("SELECT * FROM dados", engine)
        tags = pd.read_sql("SELECT * FROM tags", engine)
        
        # Limitamos a leitura de ratings a 80.000 registos para respeitar o limite de RAM do servidor grátis
        ratings = pd.read_sql("SELECT * FROM ratings LIMIT 80000", engine)
        
        # --- FORÇAR TODAS AS COLUNAS A FICAREM MINÚSCULAS (Garante compatibilidade com o Postgres) ---
        filmes.columns = filmes.columns.str.lower()
        dados_conteudo.columns = dados_conteudo.columns.str.lower()
        tags.columns = tags.columns.str.lower()
        ratings.columns = ratings.columns.str.lower()
        
        # ==========================================
        # 2. PREPARAÇÃO DO MÉTODO COLABORATIVO
        # ==========================================
        # Alterado de 'movieId' para 'movieid'
        df_colab = filmes.merge(ratings, on='movieid')
        tabela_filmes = pd.pivot_table(df_colab, index='title', columns='userid', values='rating').fillna(0)
        
        # Calculando similaridade 
        rec_colab = cosine_similarity(tabela_filmes)
        rec_df_colab = pd.DataFrame(rec_colab, columns=tabela_filmes.index, index=tabela_filmes.index)
        
        dados_globais["sim_colaborativo"] = rec_df_colab

        # ==========================================
        # 3. PREPARAÇÃO DO MÉTODO CONTENT-BASED
        # ==========================================
        # Alterado de 'movieId' para 'movieid'
        filmes['movieid'] = filmes['movieid'].astype(str)
        tags['movieid'] = tags['movieid'].astype(str)
        
        # Merges (Ajustado 'Name' para 'name' e 'movieId' para 'movieid')
        df2 = filmes.merge(dados_conteudo, left_on='title', right_on='name', how='left')
        df2 = df2.merge(tags, left_on='movieid', right_on='movieid', how='left')
        
        # Tratamento de Nulos
        df2 = df2.fillna('')
        
        # Feature Engineering (Sopa de palavras - Ajustado para colunas minúsculas)
        df2['Infos'] = (
            df2['genres'] + " " + 
            df2['directors_cast'].astype(str) + " " + 
            df2['discription'].astype(str) + " " + 
            df2['tag'].astype(str)
        )
        
        df_conteudo_unico = df2.drop_duplicates(subset=['title']).reset_index(drop=True)
        
        vec = TfidfVectorizer(stop_words='english')
        tfidf = vec.fit_transform(df_conteudo_unico['Infos'])
        
        sim_cont = cosine_similarity(tfidf)
        sim_df_cont = pd.DataFrame(sim_cont, columns=df_conteudo_unico['title'], index=df_conteudo_unico['title'])
        
        dados_globais["sim_conteudo"] = sim_df_cont
        print("✔️ Todos os modelos de IA foram treinados e carregados com sucesso do banco de dados!")
        
    except Exception as e:
        print(f"❌ Erro crítico ao carregar dados do banco: {str(e)}")

# Evento de inicialização do FastAPI
@app.on_event("startup")
async def startup_event():
    carregar_dados()

# ==========================================
# ROTAS DA API
# ==========================================

@app.get("/")
def home():
    return {"mensagem": "API de Recomendação de Filmes Online funcionando via Banco de Dados PostgreSQL!"}

@app.get("/recomendacao/colaborativa/{nome_filme}")
def recomendar_colaborativo(nome_filme: str):
    df_sim = dados_globais["sim_colaborativo"]
    
    if df_sim is None or nome_filme not in df_sim.index:
        raise HTTPException(status_code=404, detail="Filme não encontrado na base colaborativa.")
    
    recomendacoes = df_sim[nome_filme].sort_values(ascending=False).iloc[1:11]
    
    return {
        "filme_origem": nome_filme,
        "metodo": "Colaborativo (User Ratings)",
        "recomendacoes": recomendacoes.to_dict()
    }

@app.get("/recomendacao/conteudo/{nome_filme}")
def recomendar_conteudo(nome_filme: str):
    df_sim = dados_globais["sim_conteudo"]
    
    if df_sim is None or nome_filme not in df_sim.index:
        raise HTTPException(status_code=404, detail="Filme não encontrado na base de conteúdo.")
    
    recomendacoes = df_sim[nome_filme].sort_values(ascending=False).iloc[1:11]
    
    return {
        "filme_origem": nome_filme,
        "metodo": "Content-Based (TF-IDF)",
        "recomendacoes": recomendacoes.to_dict()
    }