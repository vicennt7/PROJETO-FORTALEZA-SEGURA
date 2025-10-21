import spacy

# Palavras-chave para classificação de eventos
EVENT_KEYWORDS = {
    "SEGURANCA_PUBLICA": ["roubo", "assalto", "furto", "tiros", "homicídio", "latrocínio", "sequestro", "polícia", "prisão"],
    "TRANSITO_MOBILIDADE": ["acidente", "trânsito", "congestionamento", "colisão", "atropelamento", "semáforo"],
    "INFRAESTRUTURA": ["alagamento", "falta de energia", "buraco", "iluminação"],
    "SAUDE_BEM_ESTAR": ["morte", "mal súbito", "dengue", "balneabilidade"],
}

def classify_event(text):
    """Classifica o evento com base em palavras-chave."""
    text_lower = text.lower()
    for event_type, keywords in EVENT_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return event_type
    return "NAO_CLASSIFICADO"

# Carrega o modelo de linguagem
nlp = spacy.load("pt_core_news_lg")

try:
    with open("noticias.txt", "r", encoding="utf-8") as f:
        full_text = f.read()
except FileNotFoundError:
    print("Arquivo 'noticias.txt' não encontrado.")
    exit()

news_articles = full_text.split("--- SEPARADOR DE NOTÍCIA ---")
first_article_text = news_articles[0].strip()

if not first_article_text:
    print("Arquivo 'noticias.txt' vazio.")
    exit()

print("--- Análise da Primeira Notícia ---")

# Processa o texto com o spaCy
doc = nlp(first_article_text)

# 1. Extrai O QUÊ (Tipo de Evento)
event_type = classify_event(first_article_text)
print(f"\\n[O QUÊ?] - Tipo de Evento: {event_type}")

# 2. Extrai ONDE (Locais)
locations = []
for ent in doc.ents:
    if ent.label_ in ["LOC", "GPE"]:
        # Filtro simples para remover entidades que não são locais
        if ent.text.lower() not in ["ciops", "perícia forense", "google"]:
            locations.append(ent.text.strip())
# Remove duplicados
unique_locations = sorted(list(set(locations)))
print(f"\\n[ONDE?] - Locais Encontrados: {unique_locations}")


# 3. Extrai QUANDO (Datas e Horas)
dates = []
for ent in doc.ents:
    if ent.label_ == "DATE":
        dates.append(ent.text)
unique_dates = sorted(list(set(dates)))
print(f"\\n[QUANDO?] - Datas/Horas Encontradas: {unique_dates if unique_dates else 'Nenhuma data explícita encontrada.'}")

print("\\n" + "="*30 + "\\n")
