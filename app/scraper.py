import requests
from bs4 import BeautifulSoup

class ScraperNoticias:
    def __init__(self, url_alvo):
        self.url_alvo = url_alvo
        # CORRIGIDO: Pequenos ajustes no User-Agent para ficar no padrão
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        print(f"Robô Scraper inicializado para o alvo: {self.url_alvo}")

    # CORRIGIDO: A função inteira foi indentada para ficar DENTRO da classe
    def buscar_pagina(self):
        """
        Usa a biblioteca 'requests' para baixar o conteúdo HTML da página.
        """
        try:
            resposta = requests.get(self.url_alvo, headers=self.headers, timeout=10)
            resposta.raise_for_status()
            print("Página principal baixada com sucesso.") # CORRIGIDO: "pint" para "print"
            return resposta.text # CORRIGIDO: "reposta" para "resposta"
        except requests.exceptions.RequestException as e: # CORRIGIDO: A forma de chamar a exceção
            print(f"Erro ao buscar a página: {e}")
            return None # CORRIGIDO: "Nome" para "None"

# Este bloco fica fora da classe
if __name__ == "__main__":
    URL_ALVO = "https://g1.globo.com/ce/ceara/"
    
    print(f"--- Iniciando teste do robô para o alvo: {URL_ALVO} ---")
    
    meu_robo = ScraperNoticias(URL_ALVO) # CORRIGIDO: "menu_robo" para "meu_robo"
    html_da_pagina = meu_robo.buscar_pagina()

    if html_da_pagina:
        print("\n--- CÓDIGO HTML DA PÁGINA (amostra inicial) ---")
        print(html_da_pagina[:1000])
    else:
        print("\n--- A busca pela página falhou. Verifique a conexão ou a URL. ---")