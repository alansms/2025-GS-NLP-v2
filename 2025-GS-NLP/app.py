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
import subprocess
import pickle  # Adicionado para persistência de objetos

# Inicialização de variáveis de sessão para persistência
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False
if 'ultima_atualizacao_manual' not in st.session_state:
    st.session_state.ultima_atualizacao_manual = None
if 'dados_persistidos' not in st.session_state:
    st.session_state.dados_persistidos = None
if 'forcar_atualizacao' not in st.session_state:
    st.session_state.forcar_atualizacao = False

# Verificação e instalação automática de dependências
try:
    import plotly.express as px
except ImportError:
    st.warning("Instalando a biblioteca Plotly. Por favor, aguarde...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
    import plotly.express as px

try:
    import streamlit_folium as st_folium
except ImportError:
    st.warning("Instalando a biblioteca streamlit-folium. Por favor, aguarde...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit-folium"])
    import streamlit_folium as st_folium

try:
    import matplotlib.pyplot as plt
except ImportError:
    st.warning("Instalando a biblioteca matplotlib. Por favor, aguarde...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt

from io import BytesIO
import logging
import traceback
import sys

# Importação da classe ConfigTwitter
from coleta_twitter_api import ConfigTwitter

# Importa as funções de correção para garantir colunas necessárias
from correcao_filtros import garantir_colunas_necessarias, aplicar_filtros_seguros

# Importa o gerenciador de configurações
from config_manager import salvar_config_twitter, carregar_config_twitter

# Importa o gerenciador de configurações
from config_manager import salvar_config_twitter, carregar_config_twitter

# Importa o gerenciador de configurações
from config_manager import salvar_config_twitter, carregar_config_twitter

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

# Importa módulos locais
sys.path.append('.')

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
        st.error(f"❌ Erro inesperado ao importar {modulo}: {str(e)}")
        return None

# Tenta importar os módulos necessários
try:
    AnalisadorSentimento = importar_com_seguranca('analise_sentimento', 'AnalisadorSentimento')
    ExtratorEntidades = importar_com_seguranca('extrator_entidades', 'ExtratorEntidades')
    ClassificadorDesastre = importar_com_seguranca('classificador_tipo', 'ClassificadorDesastre')
    from coleta_twitter_api import coletar_dados_emergencia, ConfigTwitter, ColetorTwitter
    from coleta_serper import ColetorSerper  # Importando o novo coletor Serper
    GeradorNuvemPalavras = importar_com_seguranca('wordcloud_gen', 'GeradorNuvemPalavras')
    GeradorMapaEmergencia = importar_com_seguranca('mapa', 'GeradorMapaEmergencia')
    # Importação dos novos módulos
    from nlp_relatorios import ProcessadorNLTK, GeradorRelatorios, plotly_para_streamlit
    # Importação do módulo de persistência
    from persistencia import GerenciadorPersistencia
except Exception as e:
    logger.error(f"Erro ao importar módulos: {str(e)}\n{traceback.format_exc()}")

# Inicialização do processador NLTK para relatórios
if 'processador_nltk' not in st.session_state:
    st.session_state.processador_nltk = ProcessadorNLTK()

# Função global de debug
def debug_info(mensagem, nivel='info', exception=None):
    """Registra informações de debug com vários níveis"""
    if nivel == 'info':
        logger.info(mensagem)
    elif nivel == 'warning':
        logger.warning(mensagem)
    elif nivel == 'error':
        if exception:
            logger.error(f"{mensagem}: {str(exception)}\n{traceback.format_exc()}")
        else:
            logger.error(mensagem)
    elif nivel == 'debug':
        logger.debug(mensagem)

# Decorador para monitorar funções
def monitorar_funcao(func):
    """Decorador para monitorar execução de funções"""
    def wrapper(*args, **kwargs):
        nome_funcao = func.__name__
        debug_info(f"Iniciando execução: {nome_funcao}")
        try:
            resultado = func(*args, **kwargs)
            debug_info(f"Concluído com sucesso: {nome_funcao}")
            return resultado
        except Exception as e:
            debug_info(f"Erro na execução: {nome_funcao}", nivel='error', exception=e)
            raise
    return wrapper

# CSS personalizado para estilo moderno
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #FF4B4B, #FF6B6B);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #FF4B4B;
    }
    
    .emergency-alert {
        background: #FFE6E6;
        border: 1px solid #FF4B4B;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background-color: #00FF00; }
    .status-offline { background-color: #FF0000; }
    .status-warning { background-color: #FFA500; }
    
    .sidebar-section {
        background: #F8F9FA;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .twitter-message {
        border-left: 3px solid #1DA1F2;
        background: #f8f9fa;
        padding: 10px;
        margin: 10px 0;
        border-radius: 0 5px 5px 0;
    }
    
    .high-urgency {
        border-left: 3px solid #FF4B4B;
        background: #FFE6E6;
    }
    
    .medium-urgency {
        border-left: 3px solid #FFA500;
        background: #FFF6E6;
    }
    
    .low-urgency {
        border-left: 3px solid #00C853;
        background: #E6F4EA;
    }
    
    .dashboard-card {
        background: white;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .config-section {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


class MonitorEmergencias:
    """Classe principal da aplicação de monitoramento"""
    
    def __init__(self):
        """Inicializa a aplicação"""
        debug_info("Inicializando MonitorEmergencias")
        self.arquivo_dados = 'data/mensagens_coletadas.json'
        self.erros_execucao = []

        # Inicializa o gerenciador de persistência
        self.persistencia = GerenciadorPersistencia(diretorio_cache='data/cache')

        # Inicializa variáveis de sessão
        self.inicializar_sessao()

        # Carrega dados com persistência
        self.carregar_dados_persistentes()

    @monitorar_funcao
    def inicializar_sessao(self):
        """Inicializa variáveis de sessão"""
        if 'dados_processados' not in st.session_state:
            st.session_state.dados_processados = pd.DataFrame()
        
        if 'ultima_atualizacao' not in st.session_state:
            st.session_state.ultima_atualizacao = None
        
        if 'config_twitter' not in st.session_state:
            st.session_state.config_twitter = None
        
        if 'auto_refresh' not in st.session_state:
            st.session_state.auto_refresh = False

        if 'filtro_tipo' not in st.session_state:
            st.session_state.filtro_tipo = "Todos"

        if 'filtro_urgencia' not in st.session_state:
            st.session_state.filtro_urgencia = "Todos"

        if 'filtro_periodo' not in st.session_state:
            st.session_state.filtro_periodo = "24 horas"

        if 'ultima_coleta' not in st.session_state:
            st.session_state.ultima_coleta = None

    @monitorar_funcao
    def carregar_dados(self):
        """Carrega dados do arquivo JSON"""
        try:
            debug_info(f"Tentando carregar dados de: {self.arquivo_dados}")

            # Verifica se o diretório existe
            diretorio = os.path.dirname(self.arquivo_dados)
            if not os.path.exists(diretorio) and diretorio:
                debug_info(f"Criando diretório: {diretorio}", nivel='warning')
                os.makedirs(diretorio, exist_ok=True)

            if os.path.exists(self.arquivo_dados):
                with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)
                    
                if dados_json.get('mensagens'):
                    df = pd.DataFrame(dados_json['mensagens'])
                    st.session_state.dados_processados = df
                    st.session_state.ultima_atualizacao = dados_json.get('ultima_atualizacao')
                    debug_info(f"Dados carregados com sucesso: {len(df)} mensagens")
                else:
                    debug_info("Nenhuma mensagem encontrada no arquivo", nivel='warning')
            else:
                debug_info(f"Arquivo {self.arquivo_dados} não encontrado", nivel='warning')

        except Exception as e:
            debug_info("Erro ao carregar dados", nivel='error', exception=e)
            self.erros_execucao.append(f"Erro ao carregar dados: {str(e)}")
            st.error(f"Erro ao carregar dados: {e}")
    
    @monitorar_funcao
    def salvar_dados(self, df: pd.DataFrame):
        """Salva dados no arquivo JSON"""
        try:
            debug_info(f"Salvando {len(df)} mensagens em: {self.arquivo_dados}")

            # Verifica se o diretório existe
            diretorio = os.path.dirname(self.arquivo_dados)
            if not os.path.exists(diretorio) and diretorio:
                debug_info(f"Criando diretório: {diretorio}")
                os.makedirs(diretorio, exist_ok=True)

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
                'ultima_atualizacao': datetime.now().isoformat()
            }

            with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
                json.dump(dados_json, f, ensure_ascii=False, indent=2)

            st.session_state.ultima_atualizacao = dados_json['ultima_atualizacao']
            debug_info("Dados salvos com sucesso")

        except Exception as e:
            debug_info("Erro ao salvar dados", nivel='error', exception=e)
            self.erros_execucao.append(f"Erro ao salvar dados: {str(e)}")
            st.error(f"Erro ao salvar dados: {e}")

    @monitorar_funcao
    def processar_dados_nlp(self, df: pd.DataFrame) -> pd.DataFrame:
        """Processa dados com NLP"""
        if df.empty:
            return df
        
        try:
            # Análise de sentimento
            analisador_sentimento = AnalisadorSentimento()
            
            # Classificação de desastres
            classificador = ClassificadorDesastre()
            
            # Extração de entidades
            extrator = ExtratorEntidades()
            
            dados_processados = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, row in df.iterrows():
                status_text.text(f'Processando mensagem {i+1}/{len(df)}...')
                progress_bar.progress((i + 1) / len(df))
                
                texto = row.get('texto', '')
                
                # Análise de sentimento
                resultado_sentimento = analisador_sentimento.analisar_mensagem(texto)
                
                # Classificação de tipo
                resultado_classificacao = classificador.classificar_mensagem(texto)
                
                # Extração de entidades
                resultado_entidades = extrator.extrair_todas_entidades(texto)
                
                # Combina resultados
                dados_linha = row.to_dict()
                dados_linha.update({
                    'sentimento': resultado_sentimento['sentimento'],
                    'score_sentimento': resultado_sentimento['score_composto'],
                    'nivel_urgencia': resultado_sentimento['nivel_urgencia'],
                    'score_urgencia': resultado_sentimento['score_urgencia'],
                    'tipo_desastre': resultado_classificacao['tipo_predito'],
                    'confianca_classificacao': resultado_classificacao['confianca'],
                    'telefones': resultado_entidades['telefones'],
                    'localizacoes': resultado_entidades['localizacoes'],
                    'pessoas': resultado_entidades['pessoas'],
                    'score_completude': resultado_entidades['score_completude']
                })
                
                dados_processados.append(dados_linha)
            
            progress_bar.empty()
            status_text.empty()
            
            return pd.DataFrame(dados_processados)
            
        except Exception as e:
            debug_info("Erro no processamento NLP", nivel='error', exception=e)
            st.error(f"Erro no processamento NLP: {e}")
            return df
    
    @monitorar_funcao
    def coletar_dados_tempo_real(self):
        """Coleta dados em tempo real usando a API do Twitter"""
        # Variável para controlar se usaremos dados simulados
        usar_dados_simulados = False
        mensagem_erro = ""

        try:
            if not st.session_state.config_twitter:
                st.warning("⚠️ Configuração da API do Twitter não encontrada. Configure na barra lateral.")
                usar_dados_simulados = True
                mensagem_erro = "Configuração da API do Twitter não encontrada"
            else:
                config = st.session_state.config_twitter

                # Criando o coletor
                coletor = ColetorTwitter(config)

                # Definindo termos de busca relevantes para desastres naturais
                termos_busca = [
                    "enchente", "alagamento", "inundação", "chuva forte",
                    "deslizamento", "desabamento", "desastre", "emergência",
                    "resgate", "socorro", "vítimas", "terremoto", "tremor",
                    "incêndio florestal", "seca", "estiagem", "tempestade",
                    "furacão", "ciclone", "tornado", "vendaval", "granizo",
                    "desabrigados", "soterrados"
                ]

                # Coletando mensagens
                status_msg = st.empty()
                status_msg.info("🔍 Coletando dados do Twitter...")

                with st.spinner("Aguarde, buscando mensagens..."):
                    try:
                        resultados = coletor.buscar_mensagens(termos_busca, max_resultados=100)

                        if not resultados or len(resultados) == 0:
                            status_msg.warning("⚠️ Nenhuma mensagem encontrada.")
                            usar_dados_simulados = True
                            mensagem_erro = "Nenhuma mensagem encontrada na API"
                        else:
                            status_msg.success(f"✅ {len(resultados)} mensagens coletadas!")

                            # Criar DataFrame com os resultados
                            df_novos = pd.DataFrame(resultados)

                            # Converter para o formato correto
                            if 'data_criacao' in df_novos.columns:
                                df_novos['data_criacao'] = pd.to_datetime(df_novos['data_criacao'])

                            # Processar os novos dados com NLP
                            df_processados = self.processar_dados_nlp(df_novos)

                            # Atualizar os dados existentes
                            if not st.session_state.dados_processados.empty:
                                # Verificar e remover duplicados pelo ID
                                ids_existentes = set(st.session_state.dados_processados['id'].astype(str))
                                df_processados = df_processados[~df_processados['id'].astype(str).isin(ids_existentes)]

                                if not df_processados.empty:
                                    st.session_state.dados_processados = pd.concat([st.session_state.dados_processados, df_processados], ignore_index=True)
                                    status_msg.success(f"✅ {len(df_processados)} novas mensagens adicionadas!")
                                else:
                                    status_msg.info("ℹ️ Nenhuma mensagem nova encontrada.")
                            else:
                                st.session_state.dados_processados = df_processados
                                status_msg.success(f"✅ {len(df_processados)} mensagens adicionadas!")

                            # Atualizar data da última coleta
                            st.session_state.ultima_coleta = datetime.now()
                            st.session_state.ultima_atualizacao_manual = datetime.now()

                            # Salvar os dados atualizados usando persistência
                            self.salvar_dados_persistentes(st.session_state.dados_processados)

                            return True

                    except Exception as e:
                        debug_info("Erro ao buscar mensagens da API", nivel='error', exception=e)
                        status_msg.error(f"❌ Erro ao acessar a API do Twitter: {str(e)}")
                        usar_dados_simulados = True
                        mensagem_erro = str(e)

                        # Verificar se é erro de rate limit
                        if "Rate limit exceeded" in str(e):
                            st.warning("⚠️ Limite de taxa da API excedido. Usando dados simulados.")

        except Exception as e:
            debug_info("Erro na coleta de dados", nivel='error', exception=e)
            st.error(f"❌ Erro na coleta de dados: {str(e)}")
            usar_dados_simulados = True
            mensagem_erro = str(e)

        # Se chegamos aqui, algo deu errado com a API - usar dados simulados
        if usar_dados_simulados:
            debug_info(f"Usando dados simulados devido a erro: {mensagem_erro}", nivel='warning')
            status_msg = st.empty()
            status_msg.warning(f"⚠️ Usando dados simulados devido a problemas com a API do Twitter: {mensagem_erro}")

            try:
                # Importar o simulador
                from simulador_dados import SimuladorDados

                with st.spinner("Gerando dados simulados para desenvolvimento..."):
                    simulador = SimuladorDados()
                    num_mensagens = 30  # Número razoável de mensagens simuladas

                    # Gerar dados simulados
                    df_simulados = simulador.gerar_dados_simulados(num_mensagens)

                    # Atualizar os dados existentes
                    if not st.session_state.dados_processados.empty:
                        # Verificar e remover duplicados pelo ID
                        ids_existentes = set(st.session_state.dados_processados['id'].astype(str))
                        df_novos_simulados = df_simulados[~df_simulados['id'].astype(str).isin(ids_existentes)]

                        if not df_novos_simulados.empty:
                            st.session_state.dados_processados = pd.concat(
                                [st.session_state.dados_processados, df_novos_simulados],
                                ignore_index=True
                            )
                            status_msg.info(f"ℹ️ {len(df_novos_simulados)} mensagens simuladas adicionadas para teste.")
                        else:
                            status_msg.info("ℹ️ Nenhuma nova mensagem simulada adicionada.")
                    else:
                        st.session_state.dados_processados = df_simulados
                        status_msg.info(f"ℹ️ {len(df_simulados)} mensagens simuladas adicionadas para teste.")

                    # Atualizar data da última coleta
                    st.session_state.ultima_coleta = datetime.now()
                    st.session_state.ultima_atualizacao_manual = datetime.now()

                    # Salvar os dados atualizados usando persistência
                    self.salvar_dados_persistentes(st.session_state.dados_processados)

                    # Adicionar indicador visual de modo simulação
                    st.sidebar.warning("⚠️ MODO SIMULAÇÃO: Usando dados fictícios")

                    return True

            except Exception as e:
                debug_info("Erro ao gerar dados simulados", nivel='error', exception=e)
                st.error(f"❌ Erro ao gerar dados simulados: {str(e)}")
                return False

    @monitorar_funcao
    def coletar_dados_serper(self):
        """Coleta dados de notícias sobre desastres via API Serper (Google News)"""
        try:
            status_msg = st.empty()
            status_msg.info("🔍 Coletando notícias sobre desastres via Serper API...")

            # Criar o coletor Serper
            coletor = ColetorSerper()

            with st.spinner("Aguarde, buscando notícias sobre desastres..."):
                # Buscar notícias
                resultados = coletor.buscar_noticias(max_resultados=50)

                if not resultados or len(resultados) == 0:
                    status_msg.warning("⚠️ Nenhuma notícia encontrada via Serper.")
                    return False

                status_msg.success(f"✅ {len(resultados)} notícias coletadas!")

                # Criar DataFrame com os resultados
                df_novos = pd.DataFrame(resultados)

                # Converter para o formato correto
                if 'data_criacao' in df_novos.columns:
                    df_novos['data_criacao'] = pd.to_datetime(df_novos['data_criacao'])

                # Processar os novos dados com NLP
                status_msg.info("🧠 Processando notícias com análise de linguagem natural...")
                df_processados = self.processar_dados_nlp(df_novos)

                # Atualizar os dados existentes
                if not st.session_state.dados_processados.empty:
                    # Verificar e remover duplicados pelo ID
                    ids_existentes = set(st.session_state.dados_processados['id'].astype(str))
                    df_processados = df_processados[~df_processados['id'].astype(str).isin(ids_existentes)]

                    if not df_processados.empty:
                        st.session_state.dados_processados = pd.concat([st.session_state.dados_processados, df_processados], ignore_index=True)
                        status_msg.success(f"✅ {len(df_processados)} novas notícias adicionadas!")
                    else:
                        status_msg.info("ℹ️ Nenhuma notícia nova encontrada.")
                else:
                    st.session_state.dados_processados = df_processados
                    status_msg.success(f"✅ {len(df_processados)} notícias adicionadas!")

                # Atualizar data da última coleta
                st.session_state.ultima_coleta = datetime.now()
                st.session_state.ultima_atualizacao_manual = datetime.now()

                # Salvar os dados atualizados usando persistência
                self.salvar_dados_persistentes(st.session_state.dados_processados)

                # Indicar que os dados incluem conteúdo do Serper
                st.sidebar.info("ℹ️ Dados incluem notícias coletadas via Google News (Serper API)")

                return True

        except Exception as e:
            debug_info("Erro na coleta de dados via Serper", nivel='error', exception=e)
            st.error(f"❌ Erro ao coletar notícias via Serper: {str(e)}")
            return False

    @monitorar_funcao
    def aplicar_filtros(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica filtros aos dados com base nos critérios selecionados"""
        if df.empty:
            return df

        # Verificar se temos a opção de mostrar dados simulados ativada
        mostrar_simulados = st.session_state.get('mostrar_dados_simulados', False)

        # Contar quantos dados reais e simulados temos
        dados_reais = 0
        if 'fonte' in df.columns:
            dados_reais = len(df[df['fonte'] != 'simulado'])
        elif 'origem' in df.columns:
            dados_reais = len(df[df['origem'] != 'simulado'])

        # Se não temos dados reais ou a opção de mostrar simulados está ativa, não filtramos os simulados
        if dados_reais == 0 or mostrar_simulados:
            if mostrar_simulados:
                st.sidebar.info("ℹ️ Modo Desenvolvimento: Exibindo dados simulados")
            elif dados_reais == 0:
                st.sidebar.warning("⚠️ Sem dados reais disponíveis: Exibindo dados simulados")
        else:
            # Caso contrário, filtramos os dados simulados
            if 'fonte' in df.columns:
                df = df[df['fonte'] != 'simulado']
            elif 'origem' in df.columns:
                df = df[df['origem'] != 'simulado']
            
        # Utilizamos a função segura para garantir que todas as colunas necessárias existam
        # e aplicamos os filtros de tipo, urgência e período selecionados
        return aplicar_filtros_seguros(df)

    @monitorar_funcao
    def construir_interface(self):
        """Constrói a interface principal do Streamlit"""
        # Título principal
        st.markdown('<div class="main-header"><h1><i class="fa fa-exclamation-triangle" style="color: red;"></i> Monitor de Emergências</h1><p>Sistema de monitoramento de mensagens emergenciais sobre desastres naturais</p></div>', unsafe_allow_html=True)

        # Barra lateral - Configurações
        with st.sidebar:
            # Logo FIAP acima das configurações - responsivo e adaptável
            st.image("FIAP-transparente.png", width=None, use_container_width=True, caption=None)

            st.title("⚙️ Configurações")

            # Seção de Atualização Manual
            st.subheader("🔄 Atualização de Dados")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Atualizar Notícias", help="Buscar notícias atualizadas sobre desastres via Google News"):
                    with st.spinner("Coletando notícias atualizadas..."):
                        if self.coletar_dados_serper():
                            st.success("✅ Notícias atualizadas com sucesso!")
                        else:
                            st.error("❌ Falha ao atualizar notícias")

            with col2:
                if st.button("Atualizar Twitter", help="Buscar novas mensagens do Twitter sobre desastres"):
                    with st.spinner("Coletando dados do Twitter..."):
                        if self.coletar_dados_tempo_real():
                            st.success("✅ Dados do Twitter atualizados!")
                        else:
                            st.error("❌ Falha ao atualizar dados do Twitter")

            # Mostrar última atualização
            if st.session_state.ultima_atualizacao_manual:
                ultima_att = st.session_state.ultima_atualizacao_manual
                st.info(f"📅 Última atualização manual: {ultima_att.strftime('%d/%m/%Y %H:%M:%S')}")

            # Separador visual
            st.markdown("---")

# Seção de Configuração API Twitter
            st.subheader("🐦 Configuração Twitter API")
            with st.expander("Configurar API do Twitter", expanded=not st.session_state.config_twitter):
                bearer_token = st.text_input("Bearer Token (obrigatório)", type="password")
                
                if st.button("Salvar configurações"):
                    if bearer_token:
                        st.session_state.config_twitter = ConfigTwitter(
                            bearer_token=bearer_token,
                            api_key="",
                            api_secret="",
                            access_token="",
                            access_token_secret=""
                        )
                        # Salvar configurações
                        from config_manager import salvar_config_twitter
                        config_dict = {
                            'bearer_token': bearer_token,
                            'api_key': "",
                            'api_secret': "",
                            'access_token': "",
                            'access_token_secret': ""
                        }
                        salvar_config_twitter(config_dict)
                        st.success("✅ Configurações salvas com sucesso!")
                    else:
                        st.error("❌ O Bearer Token é obrigatório.")
            st.subheader("🔍 Filtros")
            st.session_state.filtro_tipo = st.selectbox(
                "Tipo de desastre",
                ["Todos", "Enchente", "Deslizamento", "Terremoto", "Incêndio", "Seca", "Outro"]
            )
            st.session_state.filtro_urgencia = st.selectbox(
                "Nível de urgência",
                ["Todos", "Alto", "Médio", "Baixo"]
            )
            st.session_state.filtro_periodo = st.selectbox(
                "Período",
                ["24 horas", "7 dias", "30 dias", "Todos"]
            )

            # Controles
            st.subheader("🎮 Controles")

            # Seleção de fonte de dados
            st.write("**Fonte de dados:**")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🐦 Twitter API", help="Coletar dados em tempo real do Twitter"):
                    self.coletar_dados_tempo_real()

            with col2:
                if st.button("📰 Google News", help="Coletar notícias via Serper API (Google News)"):
                    self.coletar_dados_serper()

            # Opção para mostrar dados simulados
            st.session_state.mostrar_dados_simulados = st.checkbox(
                "Modo Desenvolvimento (mostrar dados simulados)",
                value=st.session_state.get('mostrar_dados_simulados', False),
                help="Exibe todos os dados, incluindo os simulados, útil para desenvolvimento"
            )

            st.session_state.auto_refresh = st.checkbox(
                "Atualização automática (a cada 5 min)",
                value=st.session_state.auto_refresh
            )

            # Informações
            st.subheader("ℹ️ Informações")
            if st.session_state.ultima_atualizacao:
                st.info(f"Última atualização: {st.session_state.ultima_atualizacao}")
            else:
                st.info("Nenhuma atualização realizada ainda")

            # Seção de geração de relatórios
            st.subheader("📊 Relatórios")

            relatorio_tipo = st.selectbox(
                "Tipo de Relatório",
                ["Completo", "Resumido"]
            )

            periodo_relatorio = st.selectbox(
                "Período do Relatório",
                ["Últimas 24 horas", "Última semana", "Último mês", "Todo o período"]
            )

            if st.button("📊 Gerar Relatório"):
                try:
                    if not st.session_state.dados_processados.empty:
                        with st.spinner(f"Gerando relatório {relatorio_tipo.lower()}..."):
                            gerador = GeradorRelatorios()

                            # Filtra os dados pelo período selecionado
                            df_relatorio = df_filtrado.copy()
                            if periodo_relatorio != "Todo o período":
                                agora = pd.Timestamp.now()
                                if periodo_relatorio == "Últimas 24 horas":
                                    inicio = agora - pd.Timedelta(days=1)
                                elif periodo_relatorio == "Última semana":
                                    inicio = agora - pd.Timedelta(days=7)
                                else:  # Último mês
                                    inicio = agora - pd.Timedelta(days=30)
                                df_relatorio = df_relatorio[df_relatorio['data_criacao'] >= inicio]

                            # Gera o relatório de acordo com o tipo selecionado
                            if relatorio_tipo == "Completo":
                                resultado = gerador.gerar_relatorio_completo(df_relatorio, 'relatorios')
                            else:  # Resumido
                                resultado = gerador.gerar_relatorio_resumido(df_relatorio)

                            if resultado:
                                if relatorio_tipo == "Completo":
                                    caminho_arquivo = resultado['arquivos']['relatorio_html']
                                    with open(caminho_arquivo, 'rb') as f:
                                        st.download_button(
                                            label='📊 Baixar Relatório',
                                            data=f,
                                            file_name=os.path.basename(caminho_arquivo),
                                            mime='text/html'
                                        )
                                else:  # Resumido
                                    st.json(resultado['estatisticas'])
                                    for nome, fig_base64 in resultado['visualizacoes'].items():
                                        st.image(base64.b64decode(fig_base64))

                                st.success('Relatório gerado com sucesso!')
                            else:
                                st.error('Erro ao gerar relatório: Nenhum dado retornado')

                    else:
                        st.warning("Não há dados para gerar o relatório.")
                except Exception as e:
                    st.error(f"Erro ao gerar relatório: {str(e)}")
                    logging.error(f"Erro ao gerar relatório: {str(e)}", exc_info=True)

        # Área principal - Dashboard
        if st.session_state.dados_processados.empty:
            st.info("Nenhum dado disponível. Clique em 'Atualizar dados agora' para começar.")
            return

        # Aplicar filtros
        df_filtrado = self.aplicar_filtros(st.session_state.dados_processados)

        if df_filtrado.empty:
            st.warning("Nenhum dado encontrado com os filtros selecionados.")
            return

        # Verificar colunas necessárias e processar dados se necessário
        colunas_necessarias = ['nivel_urgencia', 'tipo_desastre', 'score_urgencia', 'sentimento']
        colunas_faltando = [col for col in colunas_necessarias if col not in df_filtrado.columns]

        if colunas_faltando:
            st.warning(f"Algumas colunas necessárias estão faltando no conjunto de dados: {', '.join(colunas_faltando)}. Aplicando processamento NLP...")
            df_filtrado = self.processar_dados_nlp(df_filtrado)

            # Se ainda faltam colunas após o processamento, lidar com isso
            colunas_ainda_faltando = [col for col in colunas_necessarias if col not in df_filtrado.columns]
            if colunas_ainda_faltando:
                st.error(f"Não foi possível processar todas as colunas necessárias: {', '.join(colunas_ainda_faltando)}")
                # Adicionar valores padrão para colunas faltantes
                for col in colunas_ainda_faltando:
                    if col == 'nivel_urgencia':
                        df_filtrado['nivel_urgencia'] = 'Baixo'
                    elif col == 'tipo_desastre':
                        df_filtrado['tipo_desastre'] = 'Não classificado'
                    elif col == 'score_urgencia':
                        df_filtrado['score_urgencia'] = 0.0
                    elif col == 'sentimento':
                        df_filtrado['sentimento'] = 'neutro'

        # Métricas principais
        st.subheader("📊 Métricas Principais")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total de Mensagens", len(df_filtrado))

        with col2:
            # Verifica se a coluna existe antes de filtrar
            if 'nivel_urgencia' in df_filtrado.columns:
                alta_urgencia = len(df_filtrado[df_filtrado['nivel_urgencia'] == 'Alto'])
                st.metric("Alta Urgência", alta_urgencia)
            else:
                st.metric("Alta Urgência", "N/A")

        with col3:
            # Verifica se a coluna existe antes de usar
            if 'tipo_desastre' in df_filtrado.columns:
                tipos = df_filtrado['tipo_desastre'].value_counts()
                tipo_principal = tipos.index[0] if not tipos.empty else "N/A"
                st.metric("Tipo Principal", tipo_principal)
            else:
                st.metric("Tipo Principal", "N/A")

        with col4:
            # Verifica se a coluna existe antes de calcular
            if 'score_urgencia' in df_filtrado.columns:
                media_urgencia = df_filtrado['score_urgencia'].mean()
                st.metric("Média de Urgência", f"{media_urgencia:.2f}")
            else:
                st.metric("Média de Urgência", "N/A")

        # Gráficos e visualizações
        st.subheader("📈 Visualizações")
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Mensagens", "Gráficos", "Mapa", "Nuvem de Palavras", "Análise de Texto"])

        with tab1:
            # Lista de mensagens
            st.subheader("📝 Mensagens Recentes")
            for i, row in df_filtrado.sort_values('data_criacao', ascending=False).head(10).iterrows():
                urgencia_class = ""
                if row['nivel_urgencia'] == 'Alto':
                    urgencia_class = "high-urgency"
                elif row['nivel_urgencia'] == 'Médio':
                    urgencia_class = "medium-urgency"
                elif row['nivel_urgencia'] == 'Baixo':
                    urgencia_class = "low-urgency"

                st.markdown(f"""
                <div class="twitter-message {urgencia_class}">
                    <p><strong>Usuário:</strong> {row.get('usuario', 'Desconhecido')} | <strong>Data:</strong> {row.get('data_criacao', 'Desconhecida')} | <strong>Tipo:</strong> {row.get('tipo_desastre', 'Desconhecido')} | <strong>Urgência:</strong> {row.get('nivel_urgencia', 'Desconhecida')}</p>
                    <p>{row.get('texto', '')}</p>
                    <p><small>Localizações mencionadas: {', '.join([loc['texto'] if isinstance(loc, dict) else loc for loc in row.get('localizacoes', [])])}</small></p>
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            # Gráficos - usando novas funcionalidades do módulo de relatórios
            try:
                st.subheader("📊 Gráficos Interativos")

                # Tipo de visualização
                tipo_grafico = st.radio(
                    "Selecione o tipo de visualização:",
                    ["Tipos de Desastre", "Níveis de Urgência", "Sentimentos", "Evolução Temporal"],
                    horizontal=True
                )

                if tipo_grafico == "Tipos de Desastre":
                    fig = plotly_para_streamlit(df_filtrado, tipo='tipo')
                    st.plotly_chart(fig, use_container_width=True)

                elif tipo_grafico == "Níveis de Urgência":
                    fig = plotly_para_streamlit(df_filtrado, tipo='urgencia')
                    st.plotly_chart(fig, use_container_width=True)

                elif tipo_grafico == "Sentimentos":
                    fig = plotly_para_streamlit(df_filtrado, tipo='sentimento')
                    st.plotly_chart(fig, use_container_width=True)

                elif tipo_grafico == "Evolução Temporal":
                    fig = plotly_para_streamlit(df_filtrado, tipo='temporal')
                    st.plotly_chart(fig, use_container_width=True)

                # Estatísticas relacionadas
                with st.expander("Ver estatísticas detalhadas"):
                    # Usando o processador NLTK para estatísticas
                    processador = ProcessadorNLTK()
                    todos_textos = ' '.join(df_filtrado['texto'].fillna(''))
                    stats = processador.processar_texto_completo(todos_textos)

                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Estatísticas de texto:**")
                        st.write(f"Sentenças: {stats['numero_sentencas']}")
                        st.write(f"Tokens: {stats['numero_tokens']}")
                        st.write(f"Tokens sem stopwords: {stats['numero_tokens_sem_stopwords']}")

                    with col2:
                        st.write("**Palavras mais frequentes:**")
                        freq_df = pd.DataFrame(list(stats['frequencias'].items()),
                                              columns=['Palavra', 'Frequência'])
                        st.dataframe(freq_df.head(10))

            except Exception as e:
                st.error(f"Erro ao gerar gráficos: {str(e)}")

        with tab3:
            # Mapa de emergências
            try:
                st.subheader("🗺️ Mapa de Emergências")

                gerador_mapa = GeradorMapaEmergencia()

                # Processar as localizações no DataFrame
                df_com_coords = gerador_mapa.processar_localizacoes(df_filtrado)

                # Criar mapa base
                mapa = gerador_mapa.criar_mapa_base()

                # Adicionar marcadores ao mapa
                if not df_com_coords.empty:
                    mapa = gerador_mapa.adicionar_marcadores_emergencia(mapa, df_com_coords, mostrar_popup=True)
                    st_folium.folium_static(mapa, width=1000, height=600)
                else:
                    st.info("Não foi possível gerar o mapa. Dados de localização insuficientes.")

            except Exception as e:
                st.error(f"Erro ao gerar mapa: {str(e)}")
                debug_info("Erro ao gerar mapa", nivel='error', exception=e)

        with tab4:
            # Nuvem de palavras
            try:
                st.subheader("☁️ Nuvem de Palavras")

                col1, col2 = st.columns([1, 3])

                with col1:
                    # Opções de configuração
                    max_palavras = st.slider("Máximo de palavras", 50, 200, 100)
                    cor_fundo = st.selectbox("Cor de fundo", ["white", "black", "lightblue", "lightgray"])

                    # Filtros de tipo de desastre para nuvem
                    filtro_nuvem = st.multiselect(
                        "Filtrar por tipo (opcional)",
                        options=df_filtrado['tipo_desastre'].unique(),
                        default=[]
                    )

                    if st.button("Gerar Nuvem"):
                        df_nuvem = df_filtrado
                        if filtro_nuvem:
                            df_nuvem = df_filtrado[df_filtrado['tipo_desastre'].isin(filtro_nuvem)]

                with col2:
                    # Usando a classe nativa de nuvem de palavras
                    gerador_nuvem = GeradorNuvemPalavras()

                    # Combinar todos os textos
                    textos = df_filtrado['texto'].dropna().tolist()

                    if textos:
                        config = {
                            'max_words': max_palavras,
                            'background_color': cor_fundo,
                            'width': 800,
                            'height': 400
                        }

                        try:
                            fig, _ = gerador_nuvem.gerar_nuvem_palavras(
                                textos,
                                titulo="Nuvem de Palavras - Emergências",
                                config=config
                            )
                            st.pyplot(fig)
                        except Exception as e:
                            st.error(f"Erro ao gerar nuvem de palavras: {str(e)}")

                            # Fallback para o gerador de relatórios
                            try:
                                gerador = GeradorRelatorios()
                                fig = gerador.gerar_nuvem_palavras(df_filtrado)
                                st.pyplot(fig)
                            except Exception as e2:
                                st.error(f"Erro nos geradores de nuvem: {str(e2)}")
                    else:
                        st.info("Não há textos disponíveis para gerar a nuvem de palavras.")

            except Exception as e:
                st.error(f"Erro na aba de nuvem de palavras: {str(e)}")

        with tab5:
            # Análise de texto usando NLTK
            st.subheader("🔍 Análise de Linguagem Natural")

            col1, col2 = st.columns([1, 1])

            with col1:
                st.write("**Análise de mensagens individuais**")

                # Seleção de mensagem para análise
                mensagens_opcoes = df_filtrado['texto'].dropna().tolist()
                if mensagens_opcoes:
                    mensagem_selecionada = st.selectbox(
                        "Selecione uma mensagem para análise detalhada:",
                        options=mensagens_opcoes,
                        index=0
                    )

                    if st.button("Analisar Mensagem"):
                        try:
                            # Usando o processador NLTK para análise detalhada
                            processador = ProcessadorNLTK()
                            resultado = processador.processar_texto_completo(mensagem_selecionada)

                            st.write("**Tokens:**")
                            st.write(', '.join(resultado['tokens'][:30]) +
                                    ('...' if len(resultado['tokens']) > 30 else ''))

                            st.write("**Tokens sem stopwords:**")
                            st.write(', '.join(resultado['tokens_sem_stopwords']))

                            st.write("**Bigramas:**")
                            bigramas_str = [f"'{a}_{b}'" for a, b in resultado['bigramas'][:10]]
                            st.write(', '.join(bigramas_str) +
                                    ('...' if len(resultado['bigramas']) > 10 else ''))

                            # Sentimento e urgência da mensagem
                            linha = df_filtrado[df_filtrado['texto'] == mensagem_selecionada].iloc[0]

                            st.write("**Análise de sentimento:**")
                            st.write(f"Sentimento: {linha.get('sentimento', 'N/A')}")
                            st.write(f"Score: {linha.get('score_sentimento', 'N/A')}")

                            st.write("**Análise de urgência:**")
                            st.write(f"Nível de urgência: {linha.get('nivel_urgencia', 'N/A')}")
                            st.write(f"Score de urgência: {linha.get('score_urgencia', 'N/A')}")

                        except Exception as e:
                            st.error(f"Erro na análise da mensagem: {str(e)}")
                else:
                    st.info("Não há mensagens disponíveis para análise.")

            with col2:
                st.write("**Estatísticas do conjunto de dados**")

                try:
                    # Usando processador NLTK para estatísticas gerais
                    todos_textos = ' '.join(df_filtrado['texto'].fillna(''))

                    processador = ProcessadorNLTK()
                    stats = processador.processar_texto_completo(todos_textos)

                    # Estatísticas básicas
                    st.write(f"Total de sentenças: {stats['numero_sentencas']}")
                    st.write(f"Total de tokens: {stats['numero_tokens']}")
                    st.write(f"Tokens únicos: {len(set(stats['tokens']))}")

                    # Palavras mais frequentes
                    st.write("**Top 10 palavras mais frequentes:**")
                    freq_df = pd.DataFrame(list(stats['frequencias'].items()),
                                         columns=['Palavra', 'Frequência'])
                    st.dataframe(freq_df.head(10))

                    # Distribuição de tipos de urgência
                    st.write("**Distribuição de níveis de urgência:**")
                    urgencia_counts = df_filtrado['nivel_urgencia'].value_counts()
                    fig, ax = plt.subplots(figsize=(5, 3))
                    urgencia_counts.plot(kind='bar', ax=ax)
                    st.pyplot(fig)

                except Exception as e:
                    st.error(f"Erro na análise estatística: {str(e)}")

        # Verificação de atualização automática
        if st.session_state.auto_refresh:
            ultima_coleta = st.session_state.ultima_coleta
            agora = datetime.now()

            if ultima_coleta is None or (agora - ultima_coleta).total_seconds() >= 300:  # 5 minutos
                self.coletar_dados_tempo_real()
                st.experimental_rerun()

    @monitorar_funcao
    def carregar_dados_persistentes(self):
        """Carrega dados usando o sistema de persistência"""
        try:
            # Verifica se os dados já estão carregados na sessão atual
            if not st.session_state.dados_processados.empty and not st.session_state.forcar_atualizacao:
                debug_info("Usando dados já carregados na sessão atual")
                return True

            # Verifica se devemos forçar uma atualização
            if st.session_state.forcar_atualizacao:
                debug_info("Forçando atualização de dados")
                st.session_state.forcar_atualizacao = False
                return self.coletar_dados_tempo_real()

            # Carrega os dados do cache
            debug_info("Tentando carregar dados do cache persistente")
            df, metadata = self.persistencia.carregar_dados()

            if not df.empty:
                # Atualiza os dados na sessão
                st.session_state.dados_processados = df
                st.session_state.dados_carregados = True

                # Atualiza informações de timestamp
                ultima_atualizacao = self.persistencia.verificar_atualizacao()
                if ultima_atualizacao:
                    st.session_state.ultima_atualizacao = ultima_atualizacao

                # Atualiza outras informações da sessão
                if metadata:
                    if 'ultima_coleta' in metadata:
                        st.session_state.ultima_coleta = metadata.get('ultima_coleta')

                debug_info(f"Dados carregados do cache com sucesso: {len(df)} registros")
                return True
            else:
                debug_info("Nenhum dado encontrado no cache, tentando carregar do arquivo JSON padrão")
                # Se não encontrar dados no cache, tenta o método antigo
                self.carregar_dados()

                # Se ainda não tiver dados, coleta novos
                if st.session_state.dados_processados.empty:
                    debug_info("Nenhum dado encontrado, coletando novos dados")
                    return self.coletar_dados_tempo_real()
                else:
                    # Se tiver dados do método antigo, persiste no novo formato
                    self.salvar_dados_persistentes(st.session_state.dados_processados)
                    return True

        except Exception as e:
            debug_info("Erro ao carregar dados persistentes", nivel='error', exception=e)
            self.erros_execucao.append(f"Erro ao carregar dados persistentes: {str(e)}")
            st.error(f"Erro ao carregar dados: {e}")
            return False

    @monitorar_funcao
    def salvar_dados_persistentes(self, df: pd.DataFrame):
        """Salva dados usando o sistema de persistência"""
        if df.empty:
            debug_info("Tentativa de salvar DataFrame vazio", nivel='warning')
            return False

        try:
            # Metadata para persistir junto com os dados
            metadata = {
                'ultima_coleta': st.session_state.ultima_coleta,
                'ultima_atualizacao': datetime.now()
            }

            # Salva usando o gerenciador de persistência
            resultado = self.persistencia.salvar_dados(df, metadata)

            if resultado:
                # Atualiza informações da sessão
                st.session_state.ultima_atualizacao = datetime.now()
                st.session_state.dados_carregados = True
                debug_info(f"Dados persistidos com sucesso: {len(df)} registros")

                # Também salva no formato antigo para compatibilidade
                self.salvar_dados(df)

            return resultado

        except Exception as e:
            debug_info("Erro ao salvar dados persistentes", nivel='error', exception=e)
            self.erros_execucao.append(f"Erro ao salvar dados persistentes: {str(e)}")
            st.error(f"Erro ao salvar dados: {e}")
            return False

# Inicialização da aplicação
if __name__ == "__main__":
    try:
        monitor = MonitorEmergencias()
        monitor.construir_interface()
    except Exception as e:
        logger.error(f"Erro ao inicializar aplicação: {str(e)}\n{traceback.format_exc()}")
        st.error(f"❌ Erro ao inicializar a aplicação: {str(e)}")
        st.error("Verifique os logs para mais detalhes.")
