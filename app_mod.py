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
    filename='debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Verificação de dependências necessárias
try:
    import plotly.express as px
except ImportError:
    st.error("""
    A biblioteca 'plotly' não está instalada. 
    Por favor, execute o seguinte comando no terminal antes de iniciar o aplicativo:
    
    pip install -r requirements_mod.txt
    
    Ou instale manualmente:
    
    pip install plotly==5.17.0
    """)
    st.stop()

try:
    import streamlit_folium as st_folium
except ImportError:
    st.error("""
    A biblioteca 'streamlit-folium' não está instalada. 
    Por favor, execute o seguinte comando no terminal antes de iniciar o aplicativo:
    
    pip install -r requirements_mod.txt
    
    Ou instale manualmente:
    
    pip install streamlit-folium==0.15.1
    """)
    st.stop()

try:
    import matplotlib.pyplot as plt
except ImportError:
    st.error("""
    A biblioteca 'matplotlib' não está instalada. 
    Por favor, execute o seguinte comando no terminal antes de iniciar o aplicativo:
    
    pip install -r requirements_mod.txt
    
    Ou instale manualmente:
    
    pip install matplotlib==3.8.2
    """)
    st.stop()

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
