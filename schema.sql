-- Definição da tabela para armazenar os dados brutos coletados
CREATE TABLE DadoBruto (
    id SERIAL PRIMARY KEY,
    fonte VARCHAR(255) NOT NULL, -- Ex: 'DiarioDoNordeste', 'Twitter'
    url_noticia TEXT UNIQUE, -- A URL original da notícia ou post
    texto_completo TEXT NOT NULL, -- O conteúdo de texto extraído
    tipo_evento_classificado VARCHAR(255), -- Ex: 'SEGURANCA_PUBLICA', 'TRANSITO'
    locais_extraidos TEXT[], -- Um array de locais (bairros, ruas)
    datas_extraidas TEXT[], -- Um array de datas/horas
    data_coleta TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP -- Quando o dado foi coletado
);

-- Exemplo de como um dado seria inserido (apenas para referência):
-- INSERT INTO DadoBruto (fonte, url_noticia, texto_completo, tipo_evento_classificado, locais_extraidos, datas_extraidas)
-- VALUES (
--     'DiarioDoNordeste',
--     'https://diariodonordeste.verdesmares.com.br/seguranca/homem-sofre-mal-subito...',
--     'Um homem de cerca de 45 anos morreu...',
--     'SAUDE_BEM_ESTAR',
--     '{"avenida Washington Soares", "Fortaleza", "Aldeota", "Castelão"}',
--     '{"nesta segunda-feira"}'
-- );
