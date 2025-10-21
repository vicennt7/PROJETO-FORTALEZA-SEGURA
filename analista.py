import json
import spacy

# Palavras-chave para classificação de eventos
EVENT_KEYWORDS = {
    "SEGURANCA_PUBLICA": ["roubo", "assalto", "furto", "tiros", "homicídio", "latrocínio", "sequestro", "polícia", "prisão", "facção", "expulsão"],
    "TRANSITO_MOBILIDADE": ["acidente", "trânsito", "congestionamento", "colisão", "atropelamento", "semáforo"],
    "INFRAESTRUTURA": ["alagamento", "falta de energia", "buraco", "iluminação"],
    "SAUDE_BEM_ESTAR": ["morte", "mal súbito", "dengue", "balneabilidade", "saúde"],
}

def classify_event(text):
    text_lower = text.lower()
    for event_type, keywords in EVENT_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return event_type
    return "NAO_CLASSIFICADO"

# Carrega o modelo de linguagem
try:
    nlp = spacy.load("pt_core_news_lg")
except OSError:
    print("Modelo 'pt_core_news_lg' não encontrado. Baixando agora...")
    spacy.cli.download("pt_core_news_lg")
    nlp = spacy.load("pt_core_news_lg")


input_file = "dados_brutos.json"
output_file = "dados_analisados.json"

all_analyzed_data = []

try:
    with open(input_file, "r", encoding="utf-8") as f_in:
        source_data = json.load(f_in)

    for data in source_data:
        text = data.get("text", "")

        if not text:
            continue

        doc = nlp(text)

        # Extrai O QUÊ, ONDE, QUANDO
        event_type = classify_event(text)
        locations = list(set([ent.text.strip() for ent in doc.ents if ent.label_ in ["LOC", "GPE"] and len(ent.text.strip()) > 2]))
        dates = list(set([ent.text for ent in doc.ents if ent.label_ == "DATE"]))

        all_analyzed_data.append({
            "url": data.get("url"),
            "source": data.get("source"),
            "event_type": event_type,
            "locations": sorted(locations),
            "dates": sorted(dates)
        })

except FileNotFoundError:
    print(f"Arquivo '{input_file}' não encontrado.")
    exit()
except json.JSONDecodeError as e:
    print(f"Erro ao decodificar o JSON: {e}")
    print(f"O arquivo '{input_file}' pode estar corrompido. Tente gerá-lo novamente.")
    exit()


# Salva os dados analisados
with open(output_file, "w", encoding="utf-8") as f_out:
    json.dump(all_analyzed_data, f_out, ensure_ascii=False, indent=2)

print(f"Análise concluída. {len(all_analyzed_data)} notícias processadas e salvas em '{output_file}'.")
