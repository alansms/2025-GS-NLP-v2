"""
Monitor de Emergências - Aplicação Principal Streamlit
Sistema completo para monitoramento de mensagens emergenciais sobre desastres naturais
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import traceback
from sidebar import mostrar_sidebar

# Configuração da página - DEVE ser o primeiro comando Streamlit
st.set_page_config(
    page_title="Monitor de Emergências",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuração de logging
logging.basicConfig(
    filename='debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Logger principal
logger = logging.getLogger("monitor_emergencias")

# Função principal do aplicativo
def main():
    """Função principal do aplicativo"""
    # Título principal
    st.title("🚨 Monitor de Emergências")
    st.markdown("### Sistema de Monitoramento de Desastres Naturais em Tempo Real")

    # Mostra a barra lateral com todas as funcionalidades
    mostrar_sidebar()

    # Conteúdo principal
    if 'dados_processados' in st.session_state and not st.session_state.dados_processados.empty:
        # Tabs para diferentes visualizações
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Estatísticas", "🗺️ Mapa", "📝 Mensagens", "☁️ Nuvem de Palavras"])

        with tab1:
            st.header("Estatísticas")
            try:
                from visualizacoes import exibir_estatisticas
                exibir_estatisticas(st.session_state.dados_processados)
            except Exception as e:
                st.error(f"Erro ao exibir estatísticas: {str(e)}")

        with tab2:
            st.header("Mapa de Ocorrências")
            try:
                from mapa import GeradorMapaEmergencia
                gerador_mapa = GeradorMapaEmergencia()
                mapa = gerador_mapa.gerar_mapa(st.session_state.dados_processados)
                st_folium.folium_static(mapa)
            except Exception as e:
                st.error(f"Erro ao exibir mapa: {str(e)}")

        with tab3:
            st.header("Mensagens Recentes")
            try:
                from visualizacoes import exibir_mensagens_recentes
                exibir_mensagens_recentes(st.session_state.dados_processados)
            except Exception as e:
                st.error(f"Erro ao exibir mensagens: {str(e)}")

        with tab4:
            st.header("Nuvem de Palavras")
            try:
                from visualizacoes import exibir_nuvem_palavras
                exibir_nuvem_palavras(st.session_state.dados_processados)
            except Exception as e:
                st.error(f"Erro ao exibir nuvem de palavras: {str(e)}")
    else:
        st.info("Clique em 'Atualizar Dados' para começar")

# Executa o aplicativo
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Erro na execução do aplicativo: {str(e)}")
        logger.error(f"Erro na execução principal do aplicativo: {str(e)}\n{traceback.format_exc()}")
