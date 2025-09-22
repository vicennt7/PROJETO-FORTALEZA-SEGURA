import pandas as pd
import geopandas as gpd
import os

def realizar_analise_seguranca_de_arquivos():
    """
    Função de emergência para rodar a análise diretamente dos arquivos,
    sem usar o banco de dados.
    """
    print(">>> MODO DE EMERGÊNCIA: Lendo e analisando arquivos diretamente... <<<")
    try:
        path_bairros = os.path.join("data", "Bairros final.geojson")
        path_crimes = os.path.join("data", "policecalls.csv")

        bairros_gdf = gpd.read_file(path_bairros)
        
       
        # Simplesmente lemos o CSV. O Pandas vai usar a primeira linha como cabeçalho automaticamente.
        crime_df = pd.read_csv(path_crimes)

        crime_gdf = gpd.GeoDataFrame(
            crime_df,
            geometry=gpd.points_from_xy(crime_df['lng'], crime_df['lat']),
            crs="EPSG:4674"
        )
        
        if crime_gdf.crs != bairros_gdf.crs:
            crime_gdf = crime_gdf.to_crs(bairros_gdf.crs)

        crimes_por_bairro = gpd.sjoin(crime_gdf, bairros_gdf, how="inner", predicate="within")
        contagem_crimes = crimes_por_bairro.groupby('nome').size().reset_index(name='contagem_de_crimes')

        relatorio_final = pd.merge(bairros_gdf, contagem_crimes, on='nome', how='left')
        relatorio_final['contagem_de_crimes'] = relatorio_final['contagem_de_crimes'].fillna(0).astype(int)
        
        print(">>> Análise de arquivos concluída com sucesso! <<<")
        return relatorio_final

    except Exception as e:
        print(f"!!! ERRO NA ANÁLISE DE ARQUIVOS: {e} !!!")
        return {"error": f"Ocorreu um erro na análise de arquivos: {e}"}