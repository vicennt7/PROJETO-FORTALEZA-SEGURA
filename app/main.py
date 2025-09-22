# main.py

from fastapi import FastAPI, Response, HTTPException
import app.analise as analise
import pandas as pd
import json

app = FastAPI(title="Fortaleza Segura - Apresentação")

print(">>> API INICIADA COM A VERSÃO MAIS RECENTE DO CÓDIGO <<<")

@app.get("/")
def read_root():
    return {"status": "API de emergência funcionando!"}

@app.get("/analise_seguranca")
def get_analise_seguranca():
    """
    Retorna o GeoJSON completo com a contagem de ocorrências,
    ideal para ser usado por um aplicativo de mapa no futuro.
    """
    resultado_analise = analise.realizar_analise_seguranca_de_arquivos()
    if isinstance(resultado_analise, dict) and "error" in resultado_analise:
        raise HTTPException(status_code=500, detail=resultado_analise["error"])
    
    geojson_result = resultado_analise.to_json()
    return Response(content=geojson_result, media_type="application/json")

@app.get("/relatorio/bairros-mais-seguros")
def get_relatorio_seguranca():
    """
    Retorna um relatório simples, formatado e ordenado dos bairros,
    perfeito para visualização e apresentação.
    """
    #Roda a análise para obter os dados
    resultado_analise = analise.realizar_analise_seguranca_de_arquivos()
    if isinstance(resultado_analise, dict) and "error" in resultado_analise:
        raise HTTPException(status_code=500, detail=resultado_analise["error"])
    
    #Limpa os dados, garantindo que não há bairros sem nome
    resultado_analise = resultado_analise.dropna(subset=['nome'])
    
    #Seleciona e ordena os dados para o ranking
    relatorio_df = resultado_analise[['nome', 'contagem_de_crimes']]
    relatorio_ordenado = relatorio_df.sort_values(by='contagem_de_crimes', ascending=True).reset_index(drop=True)
    
    
    total_bairros = len(relatorio_ordenado)
    bairro_mais_seguro = relatorio_ordenado.iloc[0]['nome']
    bairro_mais_perigoso = relatorio_ordenado.iloc[-1]['nome']
    
    resumo_texto = (f"Análise de segurança completa de {total_bairros} bairros de Fortaleza. "
                    f"O bairro com menos ocorrências registradas foi {bairro_mais_seguro.title()}, "
                    f"enquanto o que apresentou mais ocorrências foi {bairro_mais_perigoso.title()}.")

    #  lista final com a posição no ranking
    ranking_final = []
    for index, row in relatorio_ordenado.iterrows():
        ranking_final.append({
            "posicao": index + 1,
            "bairro": row["nome"].title(),
            "ocorrencias": row["contagem_de_crimes"]
        })

    #relatório com a metodologia
    relatorio_final = {
        "titulo": "Relatório de Segurança dos Bairros de Fortaleza",
        "resumo": resumo_texto,
        "metodologia": {
            "fontes_de_dados": [
                "Ocorrências Criminais (policecalls.csv)",
                "Sinistros de Trânsito (sinistros-2015-2024.geojson)",
                "Mapa oficial com os limites geográficos dos bairros de Fortaleza (Bairros final.geojson)"
            ],
            "processo": [
                "1. Geolocalização: Todas as ocorrências criminais e sinistros de trânsito foram mapeados como pontos de coordenadas (latitude e longitude).",
                "2. Análise Espacial (Ponto em Polígono): O sistema realizou uma consulta geoespacial, verificando, para cada ponto de ocorrência, em qual polígono de bairro ele estava contido.",
                "3. Contagem e Ranking: As ocorrências foram agrupadas por bairro para gerar a contagem total. O ranking final é ordenado do bairro com o menor número total de incidentes para o maior."
            ]
        },
        "ranking_seguranca": ranking_final
    }
    
    #Converte para uma string JSON formatada (com quebras de linha e acentos corretos)
    json_formatado = json.dumps(relatorio_final, indent=2, ensure_ascii=False)
    
    #Retorna o JSON formatado como uma Resposta HTTP
    return Response(content=json_formatado, media_type="application/json; charset=utf-8")