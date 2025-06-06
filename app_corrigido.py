"""
Monitor de Emergências - Aplicação Principal Streamlit
Sistema completo para monitoramento de mensagens emergenciais sobre desastres naturais
"""

import streamlit as st

# Configuração da página - DEVE ser o primeiro comando Streamlit
st.set_page_config(
    page_title="Monitor de Emergências",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import json
import os
from datetime import datetime, timedelta
import time
import sys
import logging
from io import BytesIO
import traceback

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

# Logger principal
logger = logging.getLogger("monitor_emergencias")

# Verificação de dependências necessárias
try:
    import plotly.express as px
except ImportError:
    st.error("""
    A biblioteca 'plotly' não está instalada. 
    Por favor, execute o seguinte comando no terminal:
    
    pip install plotly==5.17.0
    """)
    st.stop()

try:
    import streamlit_folium as st_folium
except ImportError:
    st.error("""
    A biblioteca 'streamlit-folium' não está instalada. 
    Por favor, execute o seguinte comando no terminal:
    
    pip install streamlit-folium==0.15.1
    """)
    st.stop()

try:
    import matplotlib.pyplot as plt
except ImportError:
    st.error("""
    A biblioteca 'matplotlib' não está instalada. 
    Por favor, execute o seguinte comando no terminal:
    
    pip install matplotlib==3.8.2
    """)
    st.stop()

# Importa módulos locais
sys.path.append('.')

# Componentes do sistema
from simulador_dados import simular_mensagens
from coleta_twitter_api import coletar_tweets
from analise_sentimento import analisar_sentimento
from extrator_entidades import extrair_entidades
from classificador_tipo import classificar_tipo_desastre
from config_manager import ConfigManager
from mapa import gerar_mapa
from correcao_filtros import aplicar_filtros
from nlp_relatorios import gerar_relatorio
from wordcloud_gen import gerar_wordcloud

# Importação da classe ConfigTwitter
from coleta_twitter_api import ConfigTwitter

# Importa as funções de correção para garantir colunas necessárias
from correcao_filtros import garantir_colunas_necessarias, aplicar_filtros_seguros

# Importa o gerenciador de configurações
from config_manager import salvar_config_twitter, carregar_config_twitter

# Diretórios e arquivos
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

MENSAGENS_FILE = os.path.join(DATA_DIR, "mensagens_coletadas.json")
RESULTADOS_FILE = os.path.join(DATA_DIR, "resultados.json")

# Função para salvar dados em JSON
def salvar_json(dados, arquivo):
    try:
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        logging.error(f"Erro ao salvar arquivo {arquivo}: {str(e)}")
        return False

# Função para carregar dados do JSON
def carregar_json(arquivo):
    if not os.path.exists(arquivo):
        return []
    try:
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Erro ao carregar arquivo {arquivo}: {str(e)}")
        return []

# Função auxiliar para capturar erros de importação
def importar_com_seguranca(modulo, nome_classe=None):
    try:
        if nome_classe:
            logger.info(f"Tentando importar {nome_classe} de {modulo}")
            mod = __import__(modulo, fromlist=[nome_classe])
            classe = getattr(mod, nome_classe)
            logger.info(f"Importação de {nome_classe} bem-sucedida")
            return classe
        else:
            logger.info(f"Tentando importar {modulo}")
            mod = __import__(modulo)
            logger.info(f"Importação de {modulo} bem-sucedida")
            return mod
    except ImportError as e:
        logger.error(f"Erro ao importar {modulo}: {str(e)}")
        st.error(f"❌ Erro ao importar {modulo}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado ao importar {modulo}: {str(e)}")
