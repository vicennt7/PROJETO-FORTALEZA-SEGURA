import psycopg2
import psycopg2.extras
import os
import json

# Para usar este script, você PRECISA de um banco de dados PostgreSQL em execução.
# Configure as seguintes variáveis de ambiente com suas credenciais:
# export DB_NAME="seu_banco_de_dados"
# export DB_USER="seu_usuario"
# export DB_PASSWORD="sua_senha"
# export DB_HOST="localhost"  # ou o host onde seu DB está
# export DB_PORT="5432"      # a porta padrão do PostgreSQL

class DBManager:
    def __init__(self):
        """
        Inicializa o gerenciador de banco de dados e estabelece a conexão.
        """
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            self.cursor = self.conn.cursor()
            print("Conexão com o PostgreSQL estabelecida com sucesso.")
        except psycopg2.OperationalError as e:
            print(f"Erro ao conectar ao PostgreSQL: {e}")
            print("Verifique se o banco de dados está em execução e se as variáveis de ambiente estão corretas.")
            self.conn = None
            self.cursor = None
        except Exception as e:
            print(f"Um erro inesperado ocorreu: {e}")
            self.conn = None
            self.cursor = None

    def execute_schema(self, schema_file="schema.sql"):
        """
        Executa o arquivo de schema para criar as tabelas necessárias.
        """
        if not self.cursor:
            print("Não há conexão com o banco de dados para executar o schema.")
            return
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            self.cursor.execute(schema_sql)
            self.conn.commit()
            print(f"Schema '{schema_file}' executado com sucesso.")
        except FileNotFoundError:
            print(f"Erro: Arquivo de schema '{schema_file}' não encontrado.")
        except Exception as e:
            print(f"Erro ao executar o schema: {e}")
            self.conn.rollback()

    def insert_analyzed_data(self, json_file="dados_analisados.json"):
        """
        Insere dados de um arquivo JSON na tabela DadoBruto.
        Evita a inserção de URLs duplicadas.
        """
        if not self.cursor:
            print("Não há conexão com o banco de dados para inserir dados.")
            return 0

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Arquivo de dados '{json_file}' não encontrado.")
            return 0
        except json.JSONDecodeError:
            print(f"Erro ao decodificar o JSON do arquivo '{json_file}'.")
            return 0

        insert_query = """
        INSERT INTO DadoBruto (fonte, url_noticia, texto_completo, tipo_evento_classificado, locais_extraidos, datas_extraidas)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (url_noticia) DO NOTHING;
        """

        # Precisamos buscar o texto completo do arquivo original `dados_brutos.json`
        try:
            with open("dados_brutos.json", 'r', encoding='utf-8') as f_brutos:
                dados_brutos = {item['url']: item['text'] for item in json.load(f_brutos)}
        except FileNotFoundError:
            print("Arquivo 'dados_brutos.json' não encontrado para obter o texto completo.")
            return 0

        records_to_insert = []
        for record in data:
            url = record.get('url')
            full_text = dados_brutos.get(url, "") # Pega o texto completo correspondente

            records_to_insert.append((
                record.get('source'),
                url,
                full_text,
                record.get('event_type'),
                record.get('locations', []),
                record.get('dates', [])
            ))

        inserted_count = 0
        try:
            for record in records_to_insert:
                self.cursor.execute(insert_query, record)
                # `rowcount` nos diz se uma linha foi inserida (1) ou ignorada (0)
                inserted_count += self.cursor.rowcount
            self.conn.commit()
            print(f"Inserção concluída. {inserted_count} novos registros adicionados ao banco de dados.")
            return inserted_count
        except Exception as e:
            print(f"Erro ao inserir dados: {e}")
            self.conn.rollback()
            return 0

    def close_connection(self):
        """
        Fecha a conexão com o banco de dados.
        """
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("Conexão com o PostgreSQL fechada.")


if __name__ == '__main__':
    db_manager = DBManager()

    # Se a conexão foi estabelecida, prossiga
    if db_manager.conn:
        # 1. Garante que a estrutura do banco de dados (tabela) existe
        db_manager.execute_schema()

        # 2. Insere os dados analisados no banco de dados
        db_manager.insert_analyzed_data()

        # 3. Fecha a conexão
        db_manager.close_connection()
