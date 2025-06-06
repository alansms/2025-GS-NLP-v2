"""
Monitor de Emergências - Aplicação Principal Streamlit
Sistema completo para monitoramento de mensagens emergenciais sobre desastres naturais
"""

import streamlit as st
import pandas as pd
import logging
import traceback
from sidebar import mostrar_sidebar
from visualizacoes import (
    exibir_estatisticas,
    exibir_mapa,
    exibir_mensagens_recentes,
    exibir_nuvem_palavras
)

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
            exibir_estatisticas(st.session_state.dados_processados)

        with tab2:
            st.header("Mapa de Ocorrências")
            exibir_mapa(st.session_state.dados_processados)

        with tab3:
            st.header("Mensagens")
            exibir_mensagens_recentes(st.session_state.dados_processados)

        with tab4:
            st.header("Nuvem de Palavras")
            exibir_nuvem_palavras(st.session_state.dados_processados)
    else:
        st.info("Clique em 'Atualizar Dados' para começar")

# Executa o aplicativo
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Erro na execução do aplicativo: {str(e)}")
        logger.error(f"Erro na execução principal do aplicativo: {str(e)}\n{traceback.format_exc()}")
