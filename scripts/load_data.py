# load_data.py

import pandas as pd
import geopandas as gpd
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
import os

# Importa nossos modelos e a sessão do banco de dados do arquivo database.py
from database import SessionLocal, Bairro, Ocorrencia

def load_bairros(db: Session):
    """Lê o arquivo GeoJSON de bairros e insere no banco de dados."""
    print(">>> Iniciando carregamento de bairros...")
    
    try:
        path_bairros = os.path.join("data", "Bairros final.geojson")
        bairros_gdf = gpd.read_file(path_bairros)
        
        if 'nome' not in bairros_gdf.columns or 'geometry' not in bairros_gdf.columns:
            print("ERRO: O arquivo de bairros precisa ter as colunas 'nome' e 'geometry'.")
            return

        # Garante que os dados estão no sistema de coordenadas correto (SIRGAS 2000)
        # Se não estiver, ele converte.
        if bairros_gdf.crs.to_epsg() != 4674:
            print(f"Aviso: Convertendo CRS dos bairros de {bairros_gdf.crs} para EPSG:4674.")
            bairros_gdf = bairros_gdf.to_crs("EPSG:4674")

        for index, row in bairros_gdf.iterrows():
            # Converte a geometria para um formato que o GeoAlchemy2 entende (WKT)
            bairro_geom = WKTElement(row['geometry'].wkt, srid=4674)
            bairro_db = Bairro(nome=row['nome'], geom=bairro_geom)
            db.add(bairro_db)
        
        db.commit()
        print(f"✅ {len(bairros_gdf)} bairros carregados com sucesso!")

    except Exception as e:
        db.rollback() # Desfaz a operação em caso de erro
        print(f"❌ ERRO ao carregar bairros: {e}")

def load_ocorrencias(db: Session):
    """Lê o arquivo CSV de ocorrências e insere no banco de dados."""
    print("\n>>> Iniciando carregamento de ocorrências...")
    
    try:
        path_crimes = os.path.join("data", "policecalls.csv")
        # Lê o CSV. Como seu exemplo não tem cabeçalho, definimos os nomes das colunas.
        crime_df = pd.read_csv(path_crimes, header=None, names=['data', 'tipo_crime', 'lat', 'lon'])

        for index, row in crime_df.iterrows():
            # Cria a representação geométrica do ponto no formato WKT com o SRID correto
            ponto_geom = WKTElement(f"POINT({row['lon']} {row['lat']})", srid=4674)
            ocorrencia_db = Ocorrencia(tipo_crime=row['tipo_crime'], localizacao=ponto_geom)
            db.add(ocorrencia_db)
        
        db.commit()
        print(f"✅ {len(crime_df)} ocorrências carregadas com sucesso!")

    except Exception as e:
        db.rollback()
        print(f"❌ ERRO ao carregar ocorrências: {e}")

# Este bloco só será executado quando você rodar 'python load_data.py'
if __name__ == "__main__":
    db = SessionLocal()

    print("--- INICIANDO PROCESSO DE CARGA PARA O BANCO DE DADOS ---")
    
    print("\nLimpando tabelas existentes para evitar duplicatas...")
    try:
        db.query(Ocorrencia).delete()
        db.query(Bairro).delete()
        db.commit()
        print("Tabelas 'ocorrencias' e 'bairros' limpas.")
    except Exception as e:
        db.rollback()
        print(f"Erro ao limpar tabelas: {e}")

    # Executa as funções de carregamento
    load_bairros(db)
    load_ocorrencias(db)
    
    db.close()
    
    print("\n--- PROCESSO DE CARGA FINALIZADO ---")