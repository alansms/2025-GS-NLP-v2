"""
Módulo para gerenciar a barra lateral do Streamlit
"""
import streamlit as st
import os
import pandas as pd
from nlp_relatorios import GeradorRelatorios, filtrar_por_periodo
from desastres_serper import coletar_dados_serper
from datetime import datetime

def mostrar_sidebar():
    """Constrói e exibe a barra lateral do Streamlit"""
    with st.sidebar:
        # Logo FIAP
        st.image("FIAP-transparente.png", use_container_width=True)

        st.title("⚙️ Configurações")

        # Seção de Atualização
        st.subheader("🔄 Atualização de Dados")
        if st.button("🔄 Atualizar Dados"):
            with st.spinner("Coletando dados da Serper API..."):
                try:
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
            ["Completo", "Resumido"]
        )

        periodo_relatorio = st.selectbox(
            "Período do Relatório",
            ["Últimas 24 horas", "Última semana", "Último mês", "Todo o período"]
        )

        if st.button("📊 Gerar Relatório"):
            if 'dados_processados' in st.session_state and not st.session_state.dados_processados.empty:
                with st.spinner("Gerando relatório..."):
                    try:
                        # Cria diretório para relatórios se não existir
                        os.makedirs('relatorios', exist_ok=True)

                        # Filtra os dados pelo período selecionado usando a nova função
                        df_relatorio = filtrar_por_periodo(
                            st.session_state.dados_processados,
                            periodo_relatorio
                        )

                        # Instancia o gerador
                        gerador = GeradorRelatorios()

                        # Gera o relatório baseado no tipo selecionado
                        if relatorio_tipo == "Completo":
                            resultado = gerador.gerar_relatorio_completo(df_relatorio, 'relatorios')
                            if resultado and 'arquivos' in resultado:
                                caminho_arquivo = resultado['arquivos'].get('relatorio_html')
                                if caminho_arquivo and os.path.exists(caminho_arquivo):
                                    with open(caminho_arquivo, 'rb') as f:
                                        st.download_button(
                                            label='📊 Baixar Relatório',
                                            data=f,
                                            file_name=os.path.basename(caminho_arquivo),
                                            mime='text/html'
                                        )
                        else:  # Resumido
                            resultado = gerador.gerar_relatorio_resumido(df_relatorio)
                            if resultado:
                                # Criar arquivo HTML para o relatório resumido
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                caminho_html = os.path.join('relatorios', f"relatorio_resumido_{timestamp}.html")

                                # Converter as imagens base64 em tags HTML
                                imagens_html = ""
                                for nome, img_base64 in resultado['visualizacoes'].items():
                                    imagens_html += f"""
                                    <div class="chart">
                                        <h3>{nome.title()}</h3>
                                        <img src="data:image/png;base64,{img_base64}" style="max-width: 100%; height: auto;">
                                    </div>
                                    """

                                # Gerar HTML com as estatísticas e visualizações
                                html_content = f"""
                                <!DOCTYPE html>
                                <html>
                                <head>
                                    <meta charset="UTF-8">
                                    <title>Relatório Resumido - Monitoramento de Emergências</title>
                                    <style>
                                        body {{
                                            font-family: 'Segoe UI', Arial, sans-serif;
                                            margin: 0;
                                            padding: 20px;
                                            background-color: #f8f9fa;
                                            color: #333;
                                        }}
                                        .container {{
                                            max-width: 1200px;
                                            margin: 0 auto;
                                            background: white;
                                            padding: 20px;
                                            border-radius: 10px;
                                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                        }}
                                        h1 {{
                                            color: #e01837;
                                            text-align: center;
                                            margin-bottom: 30px;
                                        }}
                                        h2 {{
                                            color: #1a1a1a;
                                            border-bottom: 3px solid #e01837;
                                            padding-bottom: 10px;
                                            margin-top: 30px;
                                        }}
                                        .stats {{
                                            display: grid;
                                            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                                            gap: 20px;
                                            margin: 20px 0;
                                        }}
                                        .stat-box {{
                                            background: #fff;
                                            border-radius: 8px;
                                            padding: 15px;
                                            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                                        }}
                                        .chart {{
                                            background: white;
                                            border-radius: 8px;
                                            padding: 20px;
                                            margin: 20px 0;
                                            text-align: center;
                                        }}
                                        .info-geral {{
                                            display: flex;
                                            justify-content: space-between;
                                            margin-bottom: 30px;
                                        }}
                                        .info-box {{
                                            background: #fff;
                                            padding: 15px;
                                            border-radius: 8px;
                                            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                                            flex: 1;
                                            margin: 0 10px;
                                        }}
                                        .grande-numero {{
                                            font-size: 24px;
                                            font-weight: bold;
                                            color: #e01837;
                                            margin: 10px 0;
                                        }}
                                    </style>
                                </head>
                                <body>
                                    <div class="container">
                                        <h1>📊 Relatório Resumido - Monitoramento de Emergências</h1>
                                        
                                        <div class="info-geral">
                                            <div class="info-box">
                                                <h3>📋 Total de Mensagens</h3>
                                                <div class="grande-numero">{resultado['estatisticas']['Informações Gerais']['Total de Mensagens']}</div>
                                            </div>
                                            <div class="info-box">
                                                <h3>📅 Período Analisado</h3>
                                                <div class="grande-numero">{resultado['estatisticas']['Informações Gerais']['Período Analisado']}</div>
                                            </div>
                                        </div>

                                        <div class="stats">
                                            <div class="stat-box">
                                                <h3>🏷️ Tipos de Desastre</h3>
                                                {"".join([f"<p><strong>{tipo}:</strong> {qtd}</p>" for tipo, qtd in resultado['estatisticas']['Distribuição por Tipo'].items()])}
                                            </div>
                                            
                                            <div class="stat-box">
                                                <h3>🚨 Níveis de Urgência</h3>
                                                {"".join([f'<p>{"🔴" if nivel == "Alto" else "🟡" if nivel == "Médio" else "🟢"} <strong>{nivel}:</strong> {qtd}</p>' for nivel, qtd in resultado['estatisticas']['Distribuição por Urgência'].items()])}
                                            </div>
                                            
                                            <div class="stat-box">
                                                <h3>😊 Sentimentos</h3>
                                                {"".join([f'<p>{"😊" if "positivo" in sent.lower() else "😐" if "neutro" in sent.lower() else "😔"} <strong>{sent}:</strong> {qtd}</p>' for sent, qtd in resultado['estatisticas']['Distribuição por Sentimento'].items()])}
                                            </div>
                                        </div>

                                        <h2>📈 Visualizações</h2>
                                        {imagens_html}
                                    </div>
                                </body>
                                </html>
                                """

                                # Salvar o arquivo HTML
                                with open(caminho_html, 'w', encoding='utf-8') as f:
                                    f.write(html_content)

                                # Criar botão para download
                                with open(caminho_html, 'rb') as f:
                                    st.download_button(
                                        label='📊 Baixar Relatório Resumido',
                                        data=f,
                                        file_name=os.path.basename(caminho_html),
                                        mime='text/html'
                                    )

                                st.success("✅ Relatório resumido gerado com sucesso!")
                            else:
                                st.error("❌ Erro ao gerar relatório resumido: Nenhum dado retornado")

                    except Exception as e:
                        st.error(f"❌ Erro ao gerar relatório: {str(e)}")
            else:
                st.warning("⚠️ Não há dados disponíveis para gerar o relatório.")

        # Auto atualização
        st.checkbox("Atualização automática (5 min)",
                   value=st.session_state.get('auto_refresh', False),
                   key='auto_refresh')
