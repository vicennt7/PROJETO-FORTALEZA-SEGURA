# scripts/povoar_bairros.py

import sys
import os

# Adiciona o diretório raiz do projeto ao sys.path para que possamos importar do pacote 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importa as ferramentas necessárias do nosso módulo de banco de dados
from app.banco_de_dados.db_config import SessionLocal
from app.banco_de_dados.db_saida import Bairro

# Nosso "dicionário de tradução" oficial de Bairros para AIS, extraído do site da SSPDS
BAIRROS_POR_AIS = {
    1: ["Aldeota", "Cais do Porto", "Meireles", "Mucuripe", "Praia de Iracema", "Varjota", "Vicente Pinzon"],
    2: ["Bom Jardim", "Conjunto Ceará I", "Conjunto Ceará II", "Genibaú", "Granja Lisboa", "Granja Portugal", "Siqueira"],
    3: ["Ancuri", "Barroso", "Coaçu", "Conjunto Palmeiras", "Curió", "Guajeru", "Jangurussu", "Lagoa Redonda", "Messejana", "Parque Santa Maria", "Paupina", "Pedras", "São Bento"],
    4: ["Álvaro Weyne", "Carlito Pamplona", "Centro", "Farias Brito", "Jacarecanga", "Monte Castelo", "Moura Brasil", "São Gerardo", "Vila Ellery"],
    5: ["Aeroporto", "Benfica", "Bom Futuro", "Couto Fernandes", "Damas", "Demócrito Rocha", "Dendê", "Fátima", "Itaoca", "Itaperi", "Jardim América", "José Bonifácio", "Montese", "Panamericano", "Parangaba", "Parreão", "Serrinha", "Vila Peri", "Vila União"],
    6: ["Amadeu Furtado", "Antônio Bezerra", "Autran Nunes", "Bela Vista", "Bonsucesso", "Dom Lustosa", "Henrique Jorge", "João XXIII", "Jóquei Clube", "Olavo Oliveira", "Padre Andrade", "Parque Araxá", "Parquelândia", "Pici", "Presidente Kennedy", "Quintino Cunha", "Rodolfo Teófilo"],
    7: ["Aerolândia", "Alto da Balança", "Boa Vista", "Cajazeiras", "Cambeba", "Cidade dos Funcionários", "Dias Macedo", "Edson Queiroz", "Jardim das Oliveiras", "José de Alencar", "Parque Dois Irmãos", "Parque Iracema", "Parque Manibura", "Passaré", "Sabiaguaba", "Sapiranga"],
    8: ["Barra do Ceará", "Cristo Redentor", "Floresta", "Jardim Guanabara", "Jardim Iracema", "Pirambu", "Vila Velha"],
    9: ["Aracapé", "Canindezinho", "Conjunto Esperança", "Jardim Cearense", "Maraponga", "Mondubim", "Novo Mondubim", "Parque Presidente Vargas", "Parque Santa Rosa", "Parque São José", "Planalto Ayrton Senna", "Prefeito José Walter", "Vila Manoel Sátiro"],
    10: ["Cidade 2000", "Cocó", "Dionísio Torres", "Engenheiro Luciano Cavalcante", "Guararapes", "Joaquim Távora", "Lourdes", "Manuel Dias Branco", "Papicu", "Praia do Futuro I", "Praia do Futuro II", "Salinas", "São João do Tauape"]
}

def povoar_bairros():
    """
    Esta função lê o dicionário BAIRROS_POR_AIS e insere cada bairro na
    tabela 'bairros' do banco de dados, se ele ainda não existir.
    """
    print("Iniciando o povoamento da tabela de bairros...")
    db = SessionLocal()
    bairros_adicionados = 0
    try:
        # Loop através de cada par (número da AIS, lista de bairros) no dicionário
        for ais_numero, lista_bairros in BAIRROS_POR_AIS.items():
            # Loop através de cada nome de bairro na lista
            for nome_bairro in lista_bairros:
                # Verifica se o bairro já existe para evitar duplicatas
                bairro_existente = db.query(Bairro).filter(Bairro.nome == nome_bairro.title()).first()
                
                if not bairro_existente:
                    # Se não existir, cria um novo registro de Bairro
                    novo_bairro = Bairro(
                        nome=nome_bairro.title(), # Salva com a primeira letra maiúscula (ex: "Aldeota")
                        regional=f"AIS {ais_numero}" # Guarda a AIS na coluna 'regional'
                    )
                    db.add(novo_bairro) # Adiciona à "fila de salvamento"
                    bairros_adicionados += 1
        
        db.commit() # Salva todos os novos bairros de uma vez só no banco de dados
        print(f"✅ Povoamento concluído. {bairros_adicionados} novos bairros foram adicionados.")
        if bairros_adicionados == 0:
            print("(Nenhum bairro novo para adicionar. A tabela provavelmente já está povoada)")

    except Exception as e:
        print(f"❌ Ocorreu um erro durante o povoamento: {e}")
        db.rollback() # Desfaz qualquer alteração em caso de erro
    finally:
        db.close() # Garante que a conexão com o banco seja sempre encerrada

# Este bloco permite que o script seja executado diretamente pelo terminal
if __name__ == "__main__":
    povoar_bairros()