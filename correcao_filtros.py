"""
Módulo de correção para o sistema de monitoramento de desastres naturais
Este módulo contém funções para verificar e garantir que as colunas necessárias
existam no DataFrame antes de aplicar filtros ou visualizações.
"""

import pandas as pd
import streamlit as st
import logging

logger = logging.getLogger("monitor_emergencias")

def garantir_colunas_necessarias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garante que todas as colunas necessárias existam no DataFrame
    Se não existirem, cria-as com valores padrão

    Args:
        df (pd.DataFrame): DataFrame original

    Returns:
        pd.DataFrame: DataFrame com todas as colunas necessárias
    """
    # Verifica se o DataFrame está completamente vazio (sem dados e sem colunas)
    if df.empty and len(df.columns) == 0:
        logger.warning("DataFrame está completamente vazio. Retornando DataFrame vazio sem modificações.")
        return pd.DataFrame()  # Retorna um DataFrame vazio sem índice

    # Se tiver índice mas sem colunas, cria um DataFrame novo com o mesmo índice
    if df.empty and len(df.index) > 0 and len(df.columns) == 0:
        logger.warning(f"DataFrame tem índice de tamanho {len(df.index)} mas sem colunas. Criando novo DataFrame.")
        # Criar um novo DataFrame com o mesmo índice
        df_novo = pd.DataFrame(index=df.index)

        # Lista de colunas necessárias com seus valores padrão
        colunas_necessarias = {
            'nivel_urgencia': 'Médio',
            'tipo_desastre': 'Não classificado',
            'score_urgencia': 0.5,
            'sentimento': 'Neutro',
            'score_sentimento': 0.0,
            'confianca_classificacao': 0.0,
            'localizacoes': '',  # Usar string vazia em vez de lista
            'pessoas': '',       # Usar string vazia em vez de lista
            'telefones': '',     # Usar string vazia em vez de lista
            'score_completude': 0.0
        }

        # Adiciona todas as colunas necessárias com valores de tamanho apropriado
        for coluna, valor_padrao in colunas_necessarias.items():
            # Cria uma lista do mesmo tamanho do índice
            if isinstance(valor_padrao, (int, float)):
                df_novo[coluna] = [valor_padrao] * len(df.index)
            else:
                df_novo[coluna] = [valor_padrao] * len(df.index)

        logger.info("Novo DataFrame criado com todas as colunas necessárias.")
        return df_novo

    # Se o DataFrame tem dados, verificamos e adicionamos apenas as colunas faltantes
    colunas_necessarias = {
        'nivel_urgencia': 'Médio',
        'tipo_desastre': 'Não classificado',
        'score_urgencia': 0.5,
        'sentimento': 'Neutro',
        'score_sentimento': 0.0,
        'confianca_classificacao': 0.0,
        'localizacoes': '',  # Usar string vazia em vez de lista
        'pessoas': '',       # Usar string vazia em vez de lista
        'telefones': '',     # Usar string vazia em vez de lista
        'score_completude': 0.0
    }

    # Verifica cada coluna e adiciona se estiver faltando
    colunas_faltantes = []
    for coluna, valor_padrao in colunas_necessarias.items():
        if coluna not in df.columns:
            # Cria uma lista do valor padrão do mesmo tamanho do índice
            if isinstance(valor_padrao, (int, float)):
                df[coluna] = [valor_padrao] * len(df.index)
            else:
                df[coluna] = [valor_padrao] * len(df.index)
            colunas_faltantes.append(coluna)

    # Registra no log quais colunas foram adicionadas
    if colunas_faltantes:
        logger.warning(f"Colunas necessárias estão faltando no conjunto de dados: {', '.join(colunas_faltantes)}. Aplicando processamento NLP...")
        st.warning(f"Algumas colunas necessárias estão faltando no conjunto de dados: {', '.join(colunas_faltantes)}. Aplicando processamento NLP...")

    return df

def aplicar_filtros_seguros(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica filtros aos dados com base nos critérios selecionados,
    verificando primeiro se as colunas existem

    Args:
        df (pd.DataFrame): DataFrame para filtrar

    Returns:
        pd.DataFrame: DataFrame filtrado
    """
    from datetime import datetime, timedelta

    # Verifica se o DataFrame está completamente vazio ou se não tem colunas
    if df is None or df.empty or len(df.columns) == 0:
        logger.warning("DataFrame vazio ou sem colunas passado para aplicar_filtros_seguros. Retornando DataFrame vazio.")
        return pd.DataFrame()  # Retorna um DataFrame vazio sem índice

    # Garantir que todas as colunas necessárias existam
    df = garantir_colunas_necessarias(df)

    # Filtrar por tipo de desastre
    if hasattr(st.session_state, 'filtro_tipo') and st.session_state.filtro_tipo != "Todos":
        df = df[df['tipo_desastre'] == st.session_state.filtro_tipo]

    # Filtrar por nível de urgência
    if hasattr(st.session_state, 'filtro_urgencia') and st.session_state.filtro_urgencia != "Todos":
        df = df[df['nivel_urgencia'] == st.session_state.filtro_urgencia]

    # Filtrar por período
    if 'data_criacao' in df.columns and hasattr(st.session_state, 'filtro_periodo'):
        hoje = datetime.now()

        # Converter coluna para datetime se for string
        if df['data_criacao'].dtype == 'object':
            df['data_criacao'] = pd.to_datetime(df['data_criacao'], errors='coerce')

        if st.session_state.filtro_periodo == "24 horas":
            limite = hoje - timedelta(hours=24)
            df = df[df['data_criacao'] >= limite]
        elif st.session_state.filtro_periodo == "7 dias":
            limite = hoje - timedelta(days=7)
            df = df[df['data_criacao'] >= limite]
        elif st.session_state.filtro_periodo == "30 dias":
            limite = hoje - timedelta(days=30)
            df = df[df['data_criacao'] >= limite]

    return df
