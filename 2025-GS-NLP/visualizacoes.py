"""
Módulo de visualizações para o Monitor de Emergências
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from mapa import GeradorMapaEmergencia
from wordcloud_gen import GeradorNuvemPalavras
import matplotlib.pyplot as plt
from io import BytesIO

def exibir_estatisticas(df):
    """Exibe estatísticas em gráficos"""
    try:
        # Contagens
        tipos_desastres = df['tipo_desastre'].value_counts()
        sentimentos = df['sentimento'].value_counts()

        # Gráfico de pizza - Tipos de Desastre
        fig_tipos = px.pie(
            values=tipos_desastres.values,
            names=tipos_desastres.index,
            title="Distribuição por Tipo de Desastre",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_tipos, use_container_width=True)

        # Gráfico de barras - Sentimentos
        fig_sentimentos = px.bar(
            x=sentimentos.index,
            y=sentimentos.values,
            title="Distribuição por Sentimento",
            labels={'x': 'Sentimento', 'y': 'Quantidade'},
            color=sentimentos.index,
            color_discrete_map={
                'positivo': '#4CAF50',
                'neutro': '#2196F3',
                'negativo': '#F44336'
            }
        )
        st.plotly_chart(fig_sentimentos, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao exibir estatísticas: {str(e)}")

def exibir_mapa(df):
    """Exibe mapa de ocorrências"""
    try:
        gerador_mapa = GeradorMapaEmergencia()
        mapa = gerador_mapa.gerar_mapa(df)
        import streamlit_folium as st_folium
        st_folium.folium_static(mapa, width=1000, height=600)
    except Exception as e:
        st.error(f"Erro ao exibir mapa: {str(e)}")

def exibir_mensagens_recentes(df, num_mensagens=10):
    """Exibe mensagens recentes"""
    try:
        for _, row in df.sort_values('data_criacao', ascending=False).head(num_mensagens).iterrows():
            cor_fundo = '#FFE6E6' if row.get('nivel_urgencia') == 'Alto' else \
                       '#FFF6E6' if row.get('nivel_urgencia') == 'Médio' else '#E6F4EA'

            st.markdown(f"""
            <div style="padding: 15px; border-radius: 5px; margin-bottom: 10px; background-color: {cor_fundo}">
                <p><strong>Data:</strong> {row.get('data_criacao', 'N/A')} | 
                   <strong>Tipo:</strong> {row.get('tipo_desastre', 'N/A')} | 
                   <strong>Urgência:</strong> {row.get('nivel_urgencia', 'N/A')}</p>
                <p>{row.get('texto', 'N/A')}</p>
                <p><small>Localizações: {', '.join([loc.get('texto', '') for loc in row.get('localizacoes', [])])}</small></p>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro ao exibir mensagens: {str(e)}")

def exibir_nuvem_palavras(df):
    """Exibe nuvem de palavras"""
    try:
        gerador = GeradorNuvemPalavras()
        texto_completo = ' '.join(df['texto'].dropna().astype(str))
        fig = gerador.gerar_wordcloud(texto_completo)

        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        st.image(buf)
    except Exception as e:
        st.error(f"Erro ao exibir nuvem de palavras: {str(e)}")
