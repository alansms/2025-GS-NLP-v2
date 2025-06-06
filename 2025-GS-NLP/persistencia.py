"""
Gerenciador de Persistência de Dados
Módulo para persistência de dados entre sessões no Monitor de Emergências
"""

import os
import json
import pickle
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger("monitor_emergencias.persistencia")

class GerenciadorPersistencia:
    """Classe responsável por gerenciar a persistência de dados entre sessões"""

    def __init__(self, diretorio_cache='data/cache'):
        """
        Inicializa o gerenciador de persistência

        Args:
            diretorio_cache (str): Diretório para armazenar os arquivos de cache
        """
        self.diretorio_cache = diretorio_cache
        self.arquivo_dados_json = os.path.join(diretorio_cache, 'dados_emergencia.json')
        self.arquivo_cache_pickle = os.path.join(diretorio_cache, 'cache_dataframe.pkl')
        self.ultima_atualizacao = None

        # Cria o diretório de cache se não existir
        if not os.path.exists(self.diretorio_cache):
            os.makedirs(self.diretorio_cache, exist_ok=True)

    def salvar_dados(self, df, metadata=None):
        """
        Salva os dados em cache (JSON e Pickle)

        Args:
            df (pd.DataFrame): DataFrame com os dados a serem salvos
            metadata (dict, optional): Metadados adicionais

        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        if df is None or df.empty:
            logger.warning("Tentativa de salvar DataFrame vazio ou None")
            return False

        try:
            # Salva em formato JSON (para interoperabilidade)
            self._salvar_json(df, metadata)

            # Salva em formato Pickle para preservar os tipos de dados
            self._salvar_pickle(df, metadata)

            self.ultima_atualizacao = datetime.now()
            logger.info(f"Dados salvos com sucesso: {len(df)} registros")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {str(e)}")
            return False

    def _salvar_json(self, df, metadata=None):
        """Salva dados em formato JSON"""
        # Cria uma cópia do DataFrame para manipulação
        df_para_salvar = df.copy()

        # Converte colunas de data/timestamp para formato de string ISO
        for coluna in df_para_salvar.columns:
            if pd.api.types.is_datetime64_any_dtype(df_para_salvar[coluna]):
                df_para_salvar[coluna] = df_para_salvar[coluna].astype(str)

        # Função auxiliar para converter objetos não serializáveis em JSON
        def converter_para_json(obj):
            if isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            elif hasattr(obj, 'to_dict'):
                return obj.to_dict()
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            elif pd.isna(obj):
                return None
            return str(obj)

        dados_json = {
            'mensagens': json.loads(json.dumps(df_para_salvar.to_dict('records'),
                                           default=converter_para_json)),
            'ultima_atualizacao': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        with open(self.arquivo_dados_json, 'w', encoding='utf-8') as f:
            json.dump(dados_json, f, ensure_ascii=False, indent=2)

    def _salvar_pickle(self, df, metadata=None):
        """Salva dados em formato Pickle para preservar tipos"""
        dados_pickle = {
            'dataframe': df,
            'ultima_atualizacao': datetime.now(),
            'metadata': metadata or {}
        }

        with open(self.arquivo_cache_pickle, 'wb') as f:
            pickle.dump(dados_pickle, f)

    def carregar_dados(self, preferir_pickle=True):
        """
        Carrega dados do cache

        Args:
            preferir_pickle (bool): Se True, tenta carregar do pickle primeiro

        Returns:
            tuple: (DataFrame, metadata)
        """
        # Se preferir pickle e ele existir, carregar do pickle
        if preferir_pickle and os.path.exists(self.arquivo_cache_pickle):
            try:
                return self._carregar_pickle()
            except Exception as e:
                logger.warning(f"Erro ao carregar pickle, tentando JSON: {str(e)}")

        # Tenta carregar do JSON
        if os.path.exists(self.arquivo_dados_json):
            try:
                return self._carregar_json()
            except Exception as e:
                logger.error(f"Erro ao carregar JSON: {str(e)}")
                return pd.DataFrame(), {}

        # Se nenhum arquivo existir
        logger.warning("Nenhum arquivo de cache encontrado")
        return pd.DataFrame(), {}

    def _carregar_pickle(self):
        """Carrega dados do arquivo pickle"""
        with open(self.arquivo_cache_pickle, 'rb') as f:
            dados = pickle.load(f)

        self.ultima_atualizacao = dados.get('ultima_atualizacao')
        return dados['dataframe'], dados.get('metadata', {})

    def _carregar_json(self):
        """Carrega dados do arquivo JSON"""
        with open(self.arquivo_dados_json, 'r', encoding='utf-8') as f:
            dados_json = json.load(f)

        if dados_json.get('mensagens'):
            df = pd.DataFrame(dados_json['mensagens'])

            # Converte colunas de data se possível
            for coluna in df.columns:
                if coluna == 'data_criacao' or 'data' in coluna:
                    try:
                        df[coluna] = pd.to_datetime(df[coluna])
                    except:
                        pass

            metadata = dados_json.get('metadata', {})
            self.ultima_atualizacao = dados_json.get('ultima_atualizacao')
            return df, metadata

        return pd.DataFrame(), {}

    def verificar_atualizacao(self):
        """
        Verifica quando foi a última atualização

        Returns:
            datetime or None: Data da última atualização
        """
        if self.ultima_atualizacao:
            return self.ultima_atualizacao

        # Tenta obter data do arquivo mais recente
        arquivos = [self.arquivo_dados_json, self.arquivo_cache_pickle]
        datas_modificacao = []

        for arquivo in arquivos:
            if os.path.exists(arquivo):
                datas_modificacao.append(datetime.fromtimestamp(os.path.getmtime(arquivo)))

        if datas_modificacao:
            return max(datas_modificacao)

        return None

    def limpar_cache(self):
        """Limpa os arquivos de cache"""
        arquivos = [self.arquivo_dados_json, self.arquivo_cache_pickle]

        for arquivo in arquivos:
            if os.path.exists(arquivo):
                try:
                    os.remove(arquivo)
                    logger.info(f"Arquivo de cache removido: {arquivo}")
                except Exception as e:
                    logger.error(f"Erro ao remover arquivo de cache {arquivo}: {str(e)}")
