import tweepy
import os
import json

# Para usar este cliente, você PRECISA de credenciais da API do Twitter/X.
# 1. Obtenha uma conta de desenvolvedor em: https://developer.twitter.com/
# 2. Crie um novo aplicativo com acesso "Elevated" ou "Academic Research".
# 3. Gere as seguintes chaves e tokens.
# 4. A maneira mais segura de armazená-los é usando variáveis de ambiente.

# Exemplo de como configurar variáveis de ambiente (no Linux/macOS):
# export TWITTER_API_KEY="SUA_API_KEY"
# export TWITTER_API_SECRET="SEU_API_SECRET"
# export TWITTER_ACCESS_TOKEN="SEU_ACCESS_TOKEN"
# export TWITTER_ACCESS_TOKEN_SECRET="SEU_ACCESS_TOKEN_SECRET"
# export TWITTER_BEARER_TOKEN="SEU_BEARER_TOKEN"

class TwitterClient:
    def __init__(self):
        """
        Inicializa o cliente da API do Twitter usando as credenciais das variáveis de ambiente.
        """
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.bearer_token = os.getenv("TWITTER_BEARER_TOKEN")

        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret, self.bearer_token]):
            raise ValueError("Uma ou mais credenciais da API do Twitter não foram encontradas nas variáveis de ambiente.")

        try:
            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
            print("Cliente Tweepy inicializado com sucesso.")
        except Exception as e:
            print(f"Erro ao inicializar o cliente Tweepy: {e}")
            self.client = None

    def search_tweets_by_user(self, username, limit=10):
        """
        Busca os tweets mais recentes de um usuário específico.

        :param username: O @username do usuário no Twitter.
        :param limit: O número máximo de tweets a serem retornados.
        :return: Uma lista de dicionários, cada um contendo o texto e a URL de um tweet.
        """
        if not self.client:
            print("Cliente não inicializado.")
            return []

        try:
            # Primeiro, obtemos o ID do usuário a partir do nome de usuário
            user_response = self.client.get_user(username=username)
            if not user_response.data:
                print(f"Usuário '{username}' não encontrado.")
                return []
            user_id = user_response.data.id

            # Agora, buscamos os tweets do usuário pelo ID
            tweets_response = self.client.get_users_tweets(
                id=user_id,
                max_results=limit,
                tweet_fields=["created_at", "text"]
            )

            if not tweets_response.data:
                return []

            results = []
            for tweet in tweets_response.data:
                tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
                results.append({
                    "url": tweet_url,
                    "text": tweet.text,
                    "source": f"twitter_{username}"
                })
            return results

        except Exception as e:
            print(f"Erro ao buscar tweets de '{username}': {e}")
            return []

# Exemplo de uso (requer credenciais configuradas)
if __name__ == '__main__':
    try:
        twitter_client = TwitterClient()

        # Lista de perfis de interesse
        target_profiles = ["sspdsce", "pmceoficial", "guardamunfortal"]
        all_tweets = []

        for profile in target_profiles:
            print(f"\\nBuscando tweets de @{profile}...")
            tweets = twitter_client.search_tweets_by_user(profile, limit=5)
            if tweets:
                all_tweets.extend(tweets)
                for tweet in tweets:
                    print(f"  - Coletado: {tweet['text'][:80]}...")

        # Salva os dados coletados em um arquivo JSON, similar ao scraper principal
        output_file = "dados_twitter.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_tweets, f, ensure_ascii=False, indent=2)

        print(f"\\nTotal de {len(all_tweets)} tweets coletados e salvos em '{output_file}'.")

    except ValueError as e:
        print(f"ERRO: {e}")
        print("Por favor, configure as variáveis de ambiente necessárias antes de executar o script.")
