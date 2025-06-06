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

# Importação das bibliotecas necessárias
import plotly.express as px
import streamlit_folium as st_folium
import matplotlib.pyplot as plt
from io import BytesIO
import logging
import traceback

# Configuração de logging
logging.basicConfig(
    filename='debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logger principal
logger = logging.getLogger("monitor_emergencias")

# Importação dos módulos locais
try:
    from mapa import GeradorMapaEmergencia
    from analise_sentimento import AnalisadorSentimento
    from extrator_entidades import ExtratorEntidades
    from classificador_tipo import ClassificadorDesastre
    from nlp_relatorios import ProcessadorNLTK, GeradorRelatorios, plotly_para_streamlit
    from correcao_filtros import garantir_colunas_necessarias
    from wordcloud_gen import GeradorNuvemPalavras
    from config_manager import salvar_config_twitter, carregar_config_twitter
    from coleta_twitter_api import ConfigTwitter, ColetorTwitter, coletar_dados_emergencia
    from coleta_serper import ColetorSerper
    from simulador_dados import simular_dados_tempo_real
except Exception as e:
    st.error(f"Erro ao importar módulos: {str(e)}")
    logging.error(f"Erro ao importar módulos: {str(e)}\n{traceback.format_exc()}")

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
    .reportview-container {
        background-color: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background-color: #262730;
    }
    .css-1d391kg {
        background-color: #f5f7f9;
    }
    h1, h2, h3 {
        color: #1e3a8a;
    }
    .stButton>button {
        background-color: #1e3a8a;
        color: white;
    }
    .stButton>button:hover {
        background-color: #3151b5;
    }
    .alert {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .alert-info {
        background-color: #cfe2ff;
        border: 1px solid #9ec5fe;
        color: #084298;
    }
    .alert-warning {
        background-color: #fff3cd;
        border: 1px solid #ffecb5;
        color: #664d03;
    }
    .alert-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c2c7;
        color: #842029;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar dados
@monitorar_funcao
def carregar_dados(fonte="serper"):
    """
    Carrega dados para o aplicativo de monitoramento de desastres naturais.

    Args:
        fonte (str): Fonte dos dados. Opções: "serper".

    Returns:
        dict: Dicionário com as mensagens e data de atualização
    """
    try:
        # Coletar dados do Serper (Google News API)
        if fonte == "serper":
            try:
                from desastres_serper import coletar_dados_serper
                st.info("Coletando dados de notícias recentes sobre desastres naturais via Serper API...")
                return coletar_dados_serper(max_resultados_por_termo=3, salvar_arquivo=True)
            except Exception as e:
                st.error(f"Erro ao coletar dados do Serper: {str(e)}")
                logging.error(f"Erro ao coletar dados do Serper: {str(e)}\n{traceback.format_exc()}")
                return {'mensagens': [], 'ultima_atualizacao': datetime.now().isoformat()}
        # Opção padrão caso a fonte não seja reconhecida
        else:
            st.warning(f"Fonte de dados '{fonte}' não reconhecida. Usando Serper API.")
            try:
                from desastres_serper import coletar_dados_serper
                return coletar_dados_serper(max_resultados_por_termo=3, salvar_arquivo=True)
            except Exception as e:
                st.error(f"Erro ao coletar dados do Serper: {str(e)}")
                return {'mensagens': [], 'ultima_atualizacao': datetime.now().isoformat()}

    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        logging.error(f"Erro ao carregar dados: {str(e)}\n{traceback.format_exc()}")
        return {'mensagens': [], 'ultima_atualizacao': datetime.now().isoformat()}

# Função para exibir estatísticas
@monitorar_funcao
def exibir_estatisticas(df):
    try:
        # Contagem por tipo de desastre
        tipos_desastres = df['tipo_desastre'].value_counts()

        # Contagem por sentimento
        sentimentos = df['sentimento'].value_counts()

        # Cria DataFrame para o gráfico de pizza (necessário para hover_data)
        df_tipos = pd.DataFrame({
            'tipo': tipos_desastres.index,
            'quantidade': tipos_desastres.values
        })

        # Cria os gráficos com Plotly - com tooltips melhorados
        fig_tipos = px.pie(
            df_tipos,
            names='tipo',
            values='quantidade',
            title="Distribuição por Tipo de Desastre",
            color_discrete_sequence=px.colors.qualitative.Set3,
            labels={"tipo": "Tipo de Desastre", "quantidade": "Quantidade"}
        )

        # Customiza o tooltip do gráfico de pizza
        fig_tipos.update_traces(
            hovertemplate="<b>%{label}</b><br>Quantidade: %{value} ocorrências<br>(%{percent})"
        )

        # Cria DataFrame para o gráfico de barras
        df_sentimentos = pd.DataFrame({
            'sentimento': sentimentos.index,
            'quantidade': sentimentos.values
        })

        # Gráfico de barras com tooltips melhorados
        fig_sentimentos = px.bar(
            df_sentimentos,
            x='sentimento',
            y='quantidade',
            title="Distribuição por Sentimento",
            labels={'sentimento': 'Sentimento', 'quantidade': 'Quantidade de Ocorrências'},
            color='sentimento',
            color_discrete_map={
                'positivo': '#4CAF50',
                'neutro': '#2196F3',
                'negativo': '#F44336'
            },
            text='quantidade'  # Mostra valores nas barras
        )

        # Customiza o tooltip do gráfico de barras
        fig_sentimentos.update_traces(
            hovertemplate="<b>Sentimento: %{x}</b><br>Quantidade: %{y} ocorrências",
            textposition='outside'
        )

        # Exibe os gráficos
        st.plotly_chart(fig_tipos, use_container_width=True)
        st.plotly_chart(fig_sentimentos, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao exibir estatísticas: {str(e)}")
        debug_info(f"Erro ao exibir estatísticas", 'error', e)

# Função para exibir mapa
@monitorar_funcao
def exibir_mapa(df):
    try:
        # Cria uma instância do gerador de mapas
        gerador_mapa = GeradorMapaEmergencia()

        # Verifica se existem coordenadas de latitude e longitude diretamente no DataFrame
        if 'latitude' in df.columns and 'longitude' in df.columns:
            # Usa os dados existentes diretamente
            df_processado = df
        # Se não houver coordenadas, mas tiver coluna de localizações (formato do Serper)
        elif 'localizacoes' in df.columns and not df['localizacoes'].isna().all():
            # Processa os dados para extrair localizações a partir do texto e/ou nomes de cidades
            try:
                # Criar um DataFrame temporário para processamento
                df_temp = df.copy()

                # Processa os textos para extrair locais e transformar em texto para geocodificação
                df_temp['texto_processado'] = df_temp.apply(
                    lambda row: extrair_locais_para_geocodificacao(row),
                    axis=1
                )

                # Processa o DataFrame para extrair coordenadas
                df_processado = gerador_mapa.processar_localizacoes(
                    df_temp,
                    coluna_texto='texto_processado'
                )

                st.success(f"Localização processada para {len(df_processado)} eventos.")
            except Exception as proc_error:
                st.warning(f"Erro ao processar localizações: {str(proc_error)}")
                df_processado = df
        # Se tiver apenas a coluna texto, tenta extrair localizações diretamente
        elif 'texto' in df.columns:
            # Tenta processar localizações diretamente do texto
            df_processado = gerador_mapa.processar_localizacoes(df)
        else:
            st.warning("Dados de localização não disponíveis para exibir no mapa.")
            return

        # Verifica se após o processamento temos coordenadas
        if 'latitude' in df_processado.columns and 'longitude' in df_processado.columns:
            # Gera o mapa
            mapa = gerador_mapa.gerar_mapa(df_processado)

            # Exibe o mapa usando streamlit_folium
            st_folium.folium_static(mapa, width=1000, height=500)
        else:
            st.warning("Não foi possível extrair coordenadas dos dados disponíveis.")
    except Exception as e:
        st.error(f"Erro ao exibir mapa: {str(e)}")
        debug_info(f"Erro ao exibir mapa", 'error', e)

# Função auxiliar para extrair locais para geocodificação
def extrair_locais_para_geocodificacao(row):
    """Extrai informações de localização para texto usado na geocodificação"""
    texto_base = row.get('texto', '')

    # Se tiver localizações no formato Serper (lista de dicionários)
    if 'localizacoes' in row and isinstance(row['localizacoes'], list):
        for loc in row['localizacoes']:
            if isinstance(loc, dict) and 'texto' in loc:
                texto_base += f" {loc['texto']}"

    return texto_base

# Função para exibir mensagens recentes
@monitorar_funcao
def exibir_mensagens_recentes(df, num_mensagens=5):
    try:
        st.subheader("Mensagens Recentes")

        # Ordena por data (mais recentes primeiro)
        df_recentes = df.sort_values(by='data', ascending=False).head(num_mensagens)

        # Exibe cada mensagem em um card
        for i, row in df_recentes.iterrows():
            sentimento_cor = {
                'positivo': '#4CAF50',
                'neutro': '#2196F3',
                'negativo': '#F44336'
            }.get(row.get('sentimento', 'neutro'), '#2196F3')

            # Extrai informações de localização
            localizacao = "N/A"
            if 'localizacoes' in row and isinstance(row['localizacoes'], list) and row['localizacoes']:
                # Extrai o texto da primeira localização na lista
                loc_item = row['localizacoes'][0]
                if isinstance(loc_item, dict) and 'texto' in loc_item:
                    localizacao = loc_item['texto']
                    # Se houver mais localizações, adiciona-as
                    if len(row['localizacoes']) > 1:
                        loc_texts = [loc['texto'] for loc in row['localizacoes'][1:]
                                    if isinstance(loc, dict) and 'texto' in loc]
                        if loc_texts:
                            localizacao += f"; {', '.join(loc_texts)}"
            elif 'local' in row and row['local'] and row['local'] != 'N/A':
                localizacao = row['local']

            st.markdown(f"""
            <div style="padding: 15px; border-radius: 5px; margin-bottom: 10px; border-left: 5px solid {sentimento_cor}; background-color: #f8f9fa;">
                <p><strong>Data:</strong> {row.get('data', 'N/A')} | <strong>Tipo:</strong> {row.get('tipo_desastre', 'N/A')} | <strong>Sentimento:</strong> {row.get('sentimento', 'N/A')}</p>
                <p><strong>Mensagem:</strong> {row.get('texto', 'N/A')}</p>
                <p><strong>Localização:</strong> {localizacao}</p>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro ao exibir mensagens recentes: {str(e)}")
        debug_info(f"Erro ao exibir mensagens recentes", 'error', e)

# Função para gerar e exibir nuvem de palavras
@monitorar_funcao
def exibir_nuvem_palavras(df):
    try:
        st.subheader("Nuvem de Palavras")

        # Concatena todos os textos
        texto_completo = " ".join(df['texto'].dropna().astype(str).tolist())

        # Cria uma instância do gerador de nuvem de palavras
        gerador_nuvem = GeradorNuvemPalavras()

        # Gera a nuvem de palavras
        fig = gerador_nuvem.gerar_wordcloud(texto_completo)

        # Converte para formato adequado para Streamlit
        buf = BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)

        # Exibe a imagem
        st.image(buf, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao exibir nuvem de palavras: {str(e)}")
        debug_info(f"Erro ao exibir nuvem de palavras", 'error', e)

# Função personalizada para aplicar filtros
@monitorar_funcao
def aplicar_filtros_personalizados(df, data_inicio=None, data_fim=None, tipos=None, sentimentos=None, locais=None):
    """
    Aplica filtros personalizados ao DataFrame

    Args:
        df (pd.DataFrame): DataFrame original
        data_inicio: Data inicial para filtro
        data_fim: Data final para filtro
        tipos: Lista de tipos de desastre para filtrar
        sentimentos: Lista de sentimentos para filtrar
        locais: Lista de locais para filtrar

    Returns:
        pd.DataFrame: DataFrame filtrado
    """
    try:
        # Garantir que todas as colunas necessárias existam
        df = garantir_colunas_necessarias(df)

        # Cria uma cópia do DataFrame para não modificar o original
        df_filtrado = df.copy()

        # Filtro de data
        if 'data' in df_filtrado.columns and data_inicio and data_fim:
            # Converter data_inicio e data_fim para datetime
            if isinstance(data_inicio, str):
                data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
            if isinstance(data_fim, str):
                data_fim = datetime.strptime(data_fim, "%Y-%m-%d")

            # Converter coluna 'data' para datetime se for string
            if df_filtrado['data'].dtype == 'object':
                df_filtrado['data'] = pd.to_datetime(df_filtrado['data'], errors='coerce')

            # Adicionar um dia a data_fim para incluir o próprio dia
            data_fim_ajustada = data_fim + timedelta(days=1)

            # Aplicar filtro de data
            df_filtrado = df_filtrado[(df_filtrado['data'] >= data_inicio) &
                                    (df_filtrado['data'] < data_fim_ajustada)]

        # Filtro de tipo de desastre
        if 'tipo_desastre' in df_filtrado.columns and tipos and len(tipos) > 0:
            df_filtrado = df_filtrado[df_filtrado['tipo_desastre'].isin(tipos)]

        # Filtro de sentimento
        if 'sentimento' in df_filtrado.columns and sentimentos and len(sentimentos) > 0:
            df_filtrado = df_filtrado[df_filtrado['sentimento'].isin(sentimentos)]

        # Filtro de local
        if 'local' in df_filtrado.columns and locais and len(locais) > 0:
            df_filtrado = df_filtrado[df_filtrado['local'].isin(locais)]

        return df_filtrado
    except Exception as e:
        debug_info(f"Erro ao aplicar filtros personalizados", 'error', e)
        # Em caso de erro, retornar o DataFrame original
        return df

# Função para construir a barra lateral
def construir_sidebar():
    """Constrói a barra lateral do Streamlit"""
    with st.sidebar:
        # Logo FIAP
        st.image("FIAP-transparente.png", use_container_width=True)

        st.title("⚙️ Configurações")

        # Seção de Atualização Manual
        st.subheader("🔄 Atualização de Dados")
        if st.button("🔄 Atualizar dados agora"):
            with st.spinner("Coletando dados..."):
                coletar_dados()
                st.success("✅ Dados atualizados com sucesso!")

        # Mostrar última atualização
        if 'ultima_atualizacao' in st.session_state and st.session_state.ultima_atualizacao:
            st.info(f"📅 Última atualização: {st.session_state.ultima_atualizacao}")

        st.markdown("---")

        # Configurações da API do Twitter
        st.subheader("🐦 Configuração Twitter API")
        with st.expander("Configurar API do Twitter"):
            config = carregar_config_twitter()
            bearer_token = st.text_input("Bearer Token",
                                       value=config.get('bearer_token', '') if config else '',
                                       type="password")

            if st.button("💾 Salvar configurações"):
                if bearer_token:
                    config_dict = {'bearer_token': bearer_token}
                    salvar_config_twitter(config_dict)
                    st.success("✅ Configurações salvas com sucesso!")
                else:
                    st.error("❌ Bearer Token é obrigatório")

        # Filtros
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

        # Seção de geração de relatórios
        st.subheader("📊 Relatórios")

        relatorio_tipo = st.selectbox(
            "Tipo de Relatório",
            ["Completo", "Resumido", "Análise de Sentimento", "Análise de Urgência"]
        )

        periodo_relatorio = st.selectbox(
            "Período do Relatório",
            ["Últimas 24 horas", "Última semana", "Último mês", "Todo o período"]
        )

        formato_relatorio = st.radio(
            "Formato do Relatório",
            ["HTML", "PDF"],
            horizontal=True
        )

        if st.button("📑 Gerar Relatório"):
            try:
                if not st.session_state.dados_processados.empty:
                    with st.spinner(f"Gerando relatório {relatorio_tipo.lower()}..."):
                        gerador = GeradorRelatorios()

                        # Filtra os dados pelo período selecionado
                        df_relatorio = st.session_state.dados_processados.copy()
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
                            resultado = gerador.gerar_relatorio_completo(df_relatorio, 'relatorios', formato=formato_relatorio.lower())
                        elif relatorio_tipo == "Resumido":
                            resultado = gerador.gerar_relatorio_resumido(df_relatorio, 'relatorios', formato=formato_relatorio.lower())
                        elif relatorio_tipo == "Análise de Sentimento":
                            resultado = gerador.gerar_relatorio_sentimentos(df_relatorio, 'relatorios', formato=formato_relatorio.lower())
                        else:  # Análise de Urgência
                            resultado = gerador.gerar_relatorio_urgencia(df_relatorio, 'relatorios', formato=formato_relatorio.lower())

                        # Verifica qual arquivo foi gerado
                        if formato_relatorio == "HTML":
                            caminho_arquivo = resultado['arquivos'].get('relatorio_html', '')
                        else:
                            caminho_arquivo = resultado['arquivos'].get('relatorio_pdf', '')

                        if caminho_arquivo and os.path.exists(caminho_arquivo):
                            st.success(f"✅ Relatório {relatorio_tipo.lower()} gerado com sucesso!")

                            # Abre o arquivo gerado
                            with open(caminho_arquivo, 'rb') as f:
                                arquivo_bytes = f.read()

                            # Cria botão de download
                            nome_arquivo = os.path.basename(caminho_arquivo)
                            st.download_button(
                                label=f"⬇️ Download do Relatório ({formato_relatorio})",
                                data=arquivo_bytes,
                                file_name=nome_arquivo,
                                mime=f"application/{formato_relatorio.lower()}"
                            )
                        else:
                            st.error("Não foi possível encontrar o arquivo gerado.")
                else:
                    st.warning("Não há dados para gerar relatório.")
            except Exception as e:
                st.error(f"Erro ao gerar relatório: {str(e)}")
                logger.error(f"Erro ao gerar relatório: {str(e)}")

        # Auto atualização
        st.session_state.auto_refresh = st.checkbox(
            "Atualização automática (5 min)",
            value=st.session_state.get('auto_refresh', False)
        )

# Função principal do aplicativo
def main():
    # Título e descrição do app
    st.title("🚨 Monitor de Emergências")
    st.markdown("### Sistema de Monitoramento de Desastres Naturais em Tempo Real")

    # Seleção de fonte de dados
    with st.sidebar:
        st.image("FIAP-transparente.png", width=200)
        st.title("Configurações")

        fonte_dados = st.radio(
            "Fonte de dados:",
            ["Notícias (Serper API)"],
            index=0,
            help="Selecione a fonte de onde os dados serão carregados."
        )

        # Mapeamento das opções de interface para os valores da função
        fonte_map = {
            "Notícias (Serper API)": "serper"
        }

        # Botão para atualizar dados
        if st.button("Atualizar dados"):
            st.session_state['atualizar_dados'] = True

        st.divider()
        st.title("Filtros")

    # Carrega os dados com base na seleção do usuário
    if 'atualizar_dados' not in st.session_state:
        st.session_state['atualizar_dados'] = False

    with st.spinner("Carregando dados..."):
        dados = carregar_dados(fonte=fonte_map[fonte_dados])

        # Limpa o flag de atualização
        if st.session_state['atualizar_dados']:
            st.session_state['atualizar_dados'] = False
            st.success(f"Dados atualizados com sucesso! Fonte: {fonte_dados}")

    # Converte para DataFrame
    if dados and 'mensagens' in dados:
        mensagens = dados.get('mensagens', [])

        if not mensagens:
            st.warning("Nenhum dado encontrado na fonte selecionada.")
            return

        df = pd.DataFrame(mensagens)

        # Exibe informação sobre a última atualização
        ultima_atualizacao = dados.get('ultima_atualizacao', 'desconhecida')
        if isinstance(ultima_atualizacao, str):
            try:
                ultima_atualizacao = datetime.fromisoformat(ultima_atualizacao)
                st.info(f"Última atualização: {ultima_atualizacao.strftime('%d/%m/%Y %H:%M:%S')}")
            except:
                st.info(f"Última atualização: {ultima_atualizacao}")

        # Convertendo as datas de string para datetime
        if 'data_criacao' in df.columns:
            df['data'] = pd.to_datetime(df['data_criacao'])
        elif 'data' not in df.columns:
            df['data'] = pd.to_datetime('today')

        # Garantir que todas as colunas necessárias existam no DataFrame
        df = garantir_colunas_necessarias(df)
    else:
        st.error("Não foi possível carregar os dados ou formato inválido.")
        return

    # Sidebar para filtros
    with st.sidebar:
        # Filtros de data
        data_min = df['data'].min() if not df.empty and 'data' in df.columns else '2023-01-01'
        data_max = df['data'].max() if not df.empty and 'data' in df.columns else '2023-12-31'

        data_inicio = st.date_input("Data Inicial",
                                   value=datetime.strptime(data_min, "%Y-%m-%d") if isinstance(data_min, str) else data_min,
                                   min_value=datetime.strptime(data_min, "%Y-%m-%d") if isinstance(data_min, str) else data_min,
                                   max_value=datetime.strptime(data_max, "%Y-%m-%d") if isinstance(data_max, str) else data_max)

        data_fim = st.date_input("Data Final",
                               value=datetime.strptime(data_max, "%Y-%m-%d") if isinstance(data_max, str) else data_max,
                               min_value=datetime.strptime(data_min, "%Y-%m-%d") if isinstance(data_min, str) else data_min,
                               max_value=datetime.strptime(data_max, "%Y-%m-%d") if isinstance(data_max, str) else data_max)

        # Filtro de tipo de desastre
        tipos_desastre = sorted(df['tipo_desastre'].unique()) if 'tipo_desastre' in df.columns else []
        tipo_selecionado = st.multiselect("Tipo de Desastre", options=tipos_desastre)

        # Filtro de sentimento
        sentimentos = sorted(df['sentimento'].unique()) if 'sentimento' in df.columns else []
        sentimento_selecionado = st.multiselect("Sentimento", options=sentimentos)

        # Filtro de local
        locais = []
        if 'local' in df.columns:
            locais = sorted(df['local'].unique())
        elif 'localizacoes' in df.columns:
            # Extrair locais da coluna 'localizacoes' que pode conter listas de dicionários
            todos_locais = []
            for locs in df['localizacoes']:
                if isinstance(locs, list):
                    for loc in locs:
                        if isinstance(loc, dict) and 'texto' in loc:
                            todos_locais.append(loc['texto'])
                elif isinstance(locs, str) and locs:
                    todos_locais.append(locs)
            if todos_locais:
                locais = sorted(set(todos_locais))

        local_selecionado = st.multiselect("Local", options=locais)

        # Aplicar filtros
        try:
            df_filtrado = aplicar_filtros_personalizados(
                df,
                data_inicio=data_inicio,
                data_fim=data_fim,
                tipos=tipo_selecionado,
                sentimentos=sentimento_selecionado,
                locais=local_selecionado
            )

            st.info(f"Exibindo {len(df_filtrado)} de {len(df)} mensagens.")
        except Exception as e:
            st.error(f"Erro ao aplicar filtros: {str(e)}")
            debug_info(f"Erro ao aplicar filtros", 'error', e)
            df_filtrado = df

    # Exibição dos dados em abas
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Estatísticas", "🗺️ Mapa", "📝 Mensagens", "🔍 Análise"])

    with tab1:
        st.header("Estatísticas")
        exibir_estatisticas(df_filtrado)

    with tab2:
        st.header("Mapa de Ocorrências")
        exibir_mapa(df_filtrado)

    with tab3:
        st.header("Mensagens")
        exibir_mensagens_recentes(df_filtrado, 10)

    with tab4:
        st.header("Análise de Dados")
        exibir_nuvem_palavras(df_filtrado)

        # Resumo gerado por NLP
        st.subheader("Resumo das Ocorrências")
        try:
            gerador_relatorios = GeradorRelatorios()
            resumo = gerador_relatorios.gerar_resumo_eventos(df_filtrado)
            st.markdown(f"<div class='alert alert-info'>{resumo}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao gerar resumo: {str(e)}")
            debug_info(f"Erro ao gerar resumo", 'error', e)

# Executa o aplicativo
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Erro na execução do aplicativo: {str(e)}")
        debug_info(f"Erro na execução principal do aplicativo", 'error', e)
