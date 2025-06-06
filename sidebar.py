"""
Módulo para gerenciar a barra lateral do Streamlit
"""
import streamlit as st
import os
from datetime import datetime, timedelta
import pandas as pd
from nlp_relatorios import GeradorRelatorios

def mostrar_sidebar():
    """Constrói e exibe a barra lateral do Streamlit"""
    with st.sidebar:
        # Logo FIAP
        st.image("FIAP-transparente.png", use_container_width=True)

        st.title("⚙️ Configurações")

        # Seção de Atualização
        st.subheader("🔄 Atualização de Dados")
        if st.button("🔄 Atualizar Dados"):
            with st.spinner("Coletando dados..."):
                try:
                    from desastres_serper import coletar_dados_serper
                    dados = coletar_dados_serper(max_resultados_por_termo=3)
                    if dados and 'mensagens' in dados:
                        st.session_state.dados_processados = pd.DataFrame(dados['mensagens'])
                        st.success("✅ Dados atualizados!")
                    else:
                        st.error("❌ Erro ao atualizar dados")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")

        # Filtros
        st.subheader("🔍 Filtros")
        st.selectbox(
            "Tipo de desastre",
            ["Todos", "Enchente", "Deslizamento", "Terremoto", "Incêndio", "Seca", "Outro"],
            key="filtro_tipo"
        )

        st.selectbox(
            "Nível de urgência",
            ["Todos", "Alto", "Médio", "Baixo"],
            key="filtro_urgencia"
        )

        st.selectbox(
            "Período",
            ["24 horas", "7 dias", "30 dias", "Todos"],
            key="filtro_periodo"
        )

        # Seção de Relatórios
        st.markdown("---")
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
            ["HTML"],
            horizontal=True
        )

        if st.button("📑 Gerar Relatório"):
            if 'dados_processados' in st.session_state and not st.session_state.dados_processados.empty:
                with st.spinner("Gerando relatório..."):
                    try:
                        # Cria diretório para relatórios
                        os.makedirs('relatorios', exist_ok=True)

                        # Instancia o gerador
                        gerador = GeradorRelatorios()

                        # Filtra os dados pelo período
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

                        # Gera o relatório
                        if relatorio_tipo == "Completo":
                            resultado = gerador.gerar_relatorio_completo(df_relatorio, 'relatorios')
                        elif relatorio_tipo == "Resumido":
                            resultado = gerador.gerar_relatorio_resumido(df_relatorio, 'relatorios')
                        elif relatorio_tipo == "Análise de Sentimento":
                            resultado = gerador.gerar_relatorio_sentimentos(df_relatorio, 'relatorios')
                        else:
                            resultado = gerador.gerar_relatorio_urgencia(df_relatorio, 'relatorios')

                        # Prepara o download
                        caminho_arquivo = resultado['arquivos'].get('relatorio_html', '')
                        if caminho_arquivo and os.path.exists(caminho_arquivo):
                            st.success("✅ Relatório gerado com sucesso!")

                            with open(caminho_arquivo, 'rb') as f:
                                arquivo_bytes = f.read()

                            st.download_button(
                                label="⬇️ Download do Relatório",
                                data=arquivo_bytes,
                                file_name=f"relatorio_{relatorio_tipo.lower()}.html",
                                mime="text/html"
                            )
                        else:
                            st.error("Erro ao gerar o arquivo do relatório")
                    except Exception as e:
                        st.error(f"Erro ao gerar relatório: {str(e)}")
            else:
                st.warning("Não há dados para gerar relatório")
