# app/banco_de_dados/data_filter.py
"""
Módulo de Filtragem e Remoção de Duplicados
Responsável por limpar e validar dados antes do processamento
"""

import pandas as pd
import hashlib
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from app.banco_de_dados.db_saida import Evento


class DataFilter:
    """Filtrador de dados com detecção de duplicados e validação"""

    def __init__(self, db_session: Session = None):
        self.db_session = db_session
        self.stats = {
            'total_rows': 0,
            'duplicates_removed': 0,
            'invalid_rows': 0,
            'filtered_out': 0,
            'processed': 0
        }

    def generate_hash(self, row_dict: Dict, source_file: str) -> str:
        """
        Gera hash único para identificar duplicados
        """
        string_unica = str(row_dict) + source_file
        return hashlib.md5(string_unica.encode('utf-8')).hexdigest()

    def check_duplicate_in_db(self, hash_value: str) -> bool:
        """
        Verifica se o evento já existe no banco de dados
        """
        if not self.db_session:
            return False

        exists = self.db_session.query(Evento).filter(
            Evento.hash_origem == hash_value
        ).first()

        return exists is not None

    def remove_duplicates_in_dataframe(self, df: pd.DataFrame, source_file: str) -> pd.DataFrame:
        """
        Remove duplicados dentro do próprio DataFrame
        """
        initial_count = len(df)

        # Gera hash para cada linha
        df['_temp_hash'] = df.apply(
            lambda row: self.generate_hash(row.to_dict(), source_file),
            axis=1
        )

        # Remove duplicados baseado no hash
        df_unique = df.drop_duplicates(subset=['_temp_hash'], keep='first')

        # Remove coluna temporária
        df_unique = df_unique.drop(columns=['_temp_hash'])

        duplicates_count = initial_count - len(df_unique)
        self.stats['duplicates_removed'] += duplicates_count

        if duplicates_count > 0:
            print(f"   ✓ Removidos {duplicates_count} duplicados internos")

        return df_unique

    def validate_row(self, row: pd.Series, required_columns: Dict[str, str]) -> Tuple[bool, str]:
        """
        Valida se uma linha possui dados mínimos necessários
        Retorna (é_válido, motivo_da_invalidade)
        """
        # Verifica se tem município (essencial para filtrar Fortaleza)
        if 'municipio' in required_columns and required_columns['municipio']:
            municipio_val = row.get(required_columns['municipio'])
            if pd.isna(municipio_val):
                return False, "Município não informado"

        # Verifica se tem data
        if 'data' in required_columns and required_columns['data']:
            data_val = row.get(required_columns['data'])
            if pd.isna(data_val):
                return False, "Data não informada"

        # Verifica se tem natureza do crime
        if 'natureza' in required_columns and required_columns['natureza']:
            natureza_val = row.get(required_columns['natureza'])
            if pd.isna(natureza_val):
                return False, "Natureza do crime não informada"

        return True, ""

    def filter_fortaleza_only(self, df: pd.DataFrame, municipio_col: str) -> pd.DataFrame:
        """
        Filtra apenas registros de Fortaleza
        """
        if not municipio_col or municipio_col not in df.columns:
            print("   ⚠️ Coluna de município não encontrada - impossível filtrar")
            return df

        initial_count = len(df)

        # Filtra Fortaleza (case insensitive, com strip)
        df_fortaleza = df[
            df[municipio_col].astype(str).str.strip().str.lower() == 'fortaleza'
        ]

        filtered_count = initial_count - len(df_fortaleza)
        self.stats['filtered_out'] += filtered_count

        print(f"   ✓ Filtrados {len(df_fortaleza)} registros de Fortaleza ({filtered_count} de outros municípios removidos)")

        return df_fortaleza

    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza dados (strip, lowercase quando apropriado)
        """
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                df[col] = df[col].apply(
                    lambda x: str(x).strip() if pd.notna(x) else x
                )

        return df

    def filter_and_clean(
        self,
        df: pd.DataFrame,
        source_file: str,
        municipio_col: str = None,
        required_columns: Dict[str, str] = None
    ) -> pd.DataFrame:
        """
        Pipeline completo de filtragem e limpeza
        """
        self.stats['total_rows'] += len(df)

        print(f"\n[Filtrando dados de: {source_file}]")
        print(f"   Registros iniciais: {len(df)}")

        # 1. Normalizar dados
        df = self.normalize_data(df)

        # 2. Filtrar apenas Fortaleza
        if municipio_col:
            df = self.filter_fortaleza_only(df, municipio_col)

        # 3. Remover duplicados internos
        df = self.remove_duplicates_in_dataframe(df, source_file)

        # 4. Validar linhas (opcional)
        if required_columns:
            initial_count = len(df)
            valid_rows = []

            for idx, row in df.iterrows():
                is_valid, reason = self.validate_row(row, required_columns)
                if is_valid:
                    valid_rows.append(idx)
                else:
                    self.stats['invalid_rows'] += 1

            df = df.loc[valid_rows]

            if initial_count - len(df) > 0:
                print(f"   ✓ Removidas {initial_count - len(df)} linhas inválidas")

        self.stats['processed'] += len(df)
        print(f"   ✅ Registros finais processados: {len(df)}")

        return df

    def print_summary(self):
        """
        Imprime resumo das estatísticas de filtragem
        """
        print("\n" + "="*60)
        print("RESUMO DA FILTRAGEM DE DADOS")
        print("="*60)
        print(f"Total de registros analisados:     {self.stats['total_rows']}")
        print(f"Duplicados removidos:              {self.stats['duplicates_removed']}")
        print(f"Registros de outros municípios:    {self.stats['filtered_out']}")
        print(f"Registros inválidos:               {self.stats['invalid_rows']}")
        print(f"Registros processados com sucesso: {self.stats['processed']}")
        print("="*60 + "\n")
