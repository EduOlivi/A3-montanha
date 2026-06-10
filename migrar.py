import pandas as pd
from sqlalchemy import create_engine
import os

DATABASE_URL = 'postgresql://filmes_o78y_user:8Dn3409RciyqTob6w5tndAJPkyc6jBLp@dpg-d8ktig647okc73b7uq20-a.virginia-postgres.render.com/filmes_o78y'

# A Render exige que a URL comece exatamente com 'postgresql://'
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print("🔌 Conectando ao banco de dados na nuvem...")
engine = create_engine(DATABASE_URL)

# Lista dos seus arquivos CSV e os nomes que as tabelas terão no banco
arquivos_csv = {
    "Filmes.csv": "filmes",
    "Ratings.csv": "ratings",
    "Dados.csv": "dados",
    "Tags.csv": "tags"
}

print(" Iniciando a migração dos dados. Isso pode levar alguns minutos dependendo do tamanho...")

for arquivo, nome_tabela in arquivos_csv.items():
    if os.path.exists(arquivo):
        print(f"📦 Lendo {arquivo}...")
        
        # O truque mágico: se o arquivo for o Ratings (que é gigante), 
        # lemos em pedaços (chunks) para não estourar a memória do seu PC e do banco
        if arquivo == "Ratings.csv":
            chunksize = 50000
            primeira_vez = True
            for chunk in pd.read_csv(arquivo, chunksize=chunksize):
                if primeira_vez:
                    chunk.to_sql(nome_tabela, engine, if_exists='replace', index=False)
                    primeira_vez = False
                else:
                    chunk.to_sql(nome_tabela, engine, if_exists='append', index=False)
                print(f"   -> Enviando bloco de {chunksize} linhas para a tabela '{nome_tabela}'...")
        else:
            # Arquivos menores lêem de uma vez só
            df = pd.read_csv(arquivo)
            df.to_sql(nome_tabela, engine, if_exists='replace', index=False)
            print(f"   ✔️ Tabela '{nome_tabela}' criada e populada com sucesso!")
            
    else:
        print(f"⚠️ Arquivo {arquivo} não foi encontrado na pasta atual.")

print("\n MIGRACAO CONCLUÍDA COM SUCESSO! Seus dados estão na nuvem.")