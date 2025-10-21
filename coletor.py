from playwright.sync_api import sync_playwright, TimeoutError

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        print("Navegando para a página de segurança...")
        page.goto(
            "https://diariodonordeste.verdesmares.com.br/seguranca",
            timeout=60000,
            wait_until="domcontentloaded"
        )

        # Tenta clicar no botão de aceitar cookies se ele aparecer
        try:
            cookie_button = page.locator('button:has-text("Permitir todos os cookies")')
            if cookie_button.is_visible():
                print("Banner de cookies encontrado. Clicando em 'Aceitar'.")
                cookie_button.click()
        except Exception:
            print("Banner de cookies não encontrado ou não foi necessário clicar.")

        print("Simulando rolagem para ativar carregamento dinâmico...")
        page.evaluate("window.scrollBy(0, document.body.scrollHeight)")

        print("Aguardando o conteúdo das notícias carregar...")
        page.wait_for_selector('div[data-js="teaser"]', timeout=30000)
        print("Conteúdo carregado com sucesso.")

    except TimeoutError:
        print("Timeout: O conteúdo das notícias não carregou a tempo.")
        page.screenshot(path="screenshot_erro.png")
        print("Um screenshot ('screenshot_erro.png') foi salvo para análise.")
        browser.close()
        return
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        page.screenshot(path="screenshot_erro.png")
        browser.close()
        return

    link_locators = page.locator('a:has(h2.text-heading)')

    links = []
    for i in range(link_locators.count()):
        link = link_locators.nth(i).get_attribute('href')
        if link:
            if not link.startswith('http'):
                link = f"https://diariodonordeste.verdesmares.com.br{link}"
            links.append(link)

    links_to_process = links[:5]

    all_news_text = []
    print(f"Coletando texto de {len(links_to_process)} notícias...")
    for link in links_to_process:
        try:
            page.goto(link, timeout=60000, wait_until="domcontentloaded")
            # Usa o seletor correto 'div.prose'
            page.wait_for_selector('div.prose', timeout=30000)
            article_body = page.locator('div.prose').inner_text()
            all_news_text.append(article_body)
            print(f"  - Coletado de: {link}")
        except Exception as e:
            print(f"  - Falha ao coletar de {link}: {e}")

    with open("noticias.txt", "w", encoding="utf-8") as f:
        f.write("\\n\\n--- SEPARADOR DE NOTÍCIA ---\\n\\n".join(all_news_text))

    print("\\nColeta concluída! Textos salvos em 'noticias.txt'")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
