import json
import argparse
from playwright.sync_api import sync_playwright, TimeoutError
from config import SCRAPER_CONFIG

def scrape(playwright, site_name, limit=5):
    config = SCRAPER_CONFIG.get(site_name)
    if not config:
        print(f"Erro: Configuração para '{site_name}' não encontrada.")
        return []

    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        page.goto(config['start_url'], timeout=90000, wait_until="domcontentloaded")
        if config.get('cookie_button_selector'):
            try:
                cookie_button = page.locator(config['cookie_button_selector'])
                if cookie_button.is_visible(timeout=5000):
                    cookie_button.click()
            except Exception:
                pass
        page.wait_for_selector(config['list_item_selector'], timeout=30000)
    except Exception as e:
        print(f"[{site_name}] Erro ao carregar lista: {e}")
        browser.close()
        return []

    link_locators = page.locator(config['link_selector'])
    links = []
    count = min(link_locators.count(), limit)
    for i in range(count):
        link = link_locators.nth(i).get_attribute('href')
        if link:
            if not link.startswith('http'):
                link = f"{config['base_url']}{link}"
            links.append(link)

    collected_data = []
    for link in links:
        try:
            page.goto(link, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_selector(config['article_body_selector'], timeout=30000)
            text_parts = page.locator(config['article_body_selector']).all_inner_texts()
            article_body = "\\n".join(text_parts)
            collected_data.append({"url": link, "text": article_body, "source": site_name})
        except Exception as e:
            print(f"  - Falha ao coletar de {link}: {e}")

    browser.close()
    return collected_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coletor de notícias.")
    parser.add_argument("sites", nargs='+', help="Nomes dos sites para coletar", choices=SCRAPER_CONFIG.keys())
    args = parser.parse_args()

    all_sites_data = []
    with sync_playwright() as playwright:
        for site in args.sites:
            data = scrape(playwright, site)
            if data:
                all_sites_data.extend(data)

    output_file = "dados_brutos.json"
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []

    existing_data.extend(all_sites_data)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    print(f"\\nDados salvos/atualizados em '{output_file}'")
