# Configurações para cada scraper
SCRAPER_CONFIG = {
    "DiarioDoNordeste": {
        "start_url": "https://diariodonordeste.verdesmares.com.br/seguranca",
        "cookie_button_selector": 'text="Permitir todos os cookies"',
        "list_item_selector": 'div[data-js="teaser"]',
        "link_selector": 'a:has(h2.text-heading)',
        "article_body_selector": 'div.prose',  # Corrigido para o seletor correto
        "base_url": "https://diariodonordeste.verdesmares.com.br"
    },
    "OPovo": {
        "start_url": "https://www.opovo.com.br/noticias/fortaleza/",
        "cookie_button_selector": 'text="Aceitar"',
        "list_item_selector": 'div.box-listing',
        "link_selector": 'a.link-listagem',
        "article_body_selector": 'div.text-container',
        "base_url": "https://www.opovo.com.br"
    }
}
