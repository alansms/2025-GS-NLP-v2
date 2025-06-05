"""
Módulo de Processamento NLTK e Relatórios
Implementa funcionalidades adicionais de processamento de linguagem natural e geração de relatórios
"""

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.probability import FreqDist
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
try:
    import seaborn as sns
    SEABORN_DISPONIVEL = True
except ImportError:
    SEABORN_DISPONIVEL = False
    print("Aviso: Seaborn não está instalado. Alguns recursos visuais serão limitados.")
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
from io import BytesIO
import base64
from typing import Dict, List, Tuple, Optional
import json
import os
from datetime import datetime, timedelta
import logging

# Download dos recursos NLTK necessários
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('rslp', quiet=True)  # Stemmer para português
except Exception as e:
    logging.warning(f"Não foi possível baixar recursos NLTK: {e}")


class ProcessadorNLTK:
    """Classe para processamento avançado de linguagem natural com NLTK"""

    def __init__(self):
        """Inicializa o processador NLTK"""
        try:
            self.stopwords = set(stopwords.words('portuguese'))
            self.stemmer = RSLPStemmer()
        except:
            # Fallback para stopwords básicas em português
            self.stopwords = {'a', 'o', 'e', 'é', 'de', 'do', 'da', 'em', 'um', 'uma', 'para'}
            self.stemmer = None
            logging.warning("Não foi possível carregar recursos NLTK completos.")

    def tokenizar_texto(self, texto: str) -> List[str]:
        """
        Tokeniza o texto em palavras

        Args:
            texto (str): Texto para tokenizar

        Returns:
            List[str]: Lista de tokens
        """
        return word_tokenize(texto.lower(), language='portuguese')

    def tokenizar_sentencas(self, texto: str) -> List[str]:
        """
        Tokeniza o texto em sentenças

        Args:
            texto (str): Texto para tokenizar

        Returns:
            List[str]: Lista de sentenças
        """
        return sent_tokenize(texto, language='portuguese')

    def remover_stopwords(self, tokens: List[str]) -> List[str]:
        """
        Remove stopwords dos tokens

        Args:
            tokens (List[str]): Lista de tokens

        Returns:
            List[str]: Lista de tokens sem stopwords
        """
        return [token for token in tokens if token.lower() not in self.stopwords]

    def aplicar_stemming(self, tokens: List[str]) -> List[str]:
        """
        Aplica stemming nos tokens

        Args:
            tokens (List[str]): Lista de tokens

        Returns:
            List[str]: Lista de stems
        """
        if self.stemmer is None:
            return tokens

        return [self.stemmer.stem(token) for token in tokens]

    def extrair_ngrams(self, tokens: List[str], n: int = 2) -> List[str]:
        """
        Extrai n-gramas dos tokens

        Args:
            tokens (List[str]): Lista de tokens
            n (int): Tamanho do n-grama

        Returns:
            List[str]: Lista de n-gramas
        """
        return list(nltk.ngrams(tokens, n))

    def calcular_frequencia(self, tokens: List[str], top_n: int = 20) -> Dict[str, int]:
        """
        Calcula frequência das palavras

        Args:
            tokens (List[str]): Lista de tokens
            top_n (int): Número de palavras mais frequentes

        Returns:
            Dict[str, int]: Dicionário de frequências
        """
        fdist = FreqDist(tokens)
        return dict(fdist.most_common(top_n))

    def extrair_palavras_chave(self, texto: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Extrai palavras-chave usando TF-IDF simplificado

        Args:
            texto (str): Texto para analisar
            top_n (int): Número de palavras-chave para retornar

        Returns:
            List[Tuple[str, float]]: Lista de palavras-chave com scores
        """
        # Tokeniza e remove stopwords
        tokens = self.remover_stopwords(self.tokenizar_texto(texto))

        # Calcula frequência
        frequencia = FreqDist(tokens)

        # Calcula score baseado na frequência e comprimento da palavra
        # (Como aproximação simples de importância)
        palavras_chave = [(word, freq * (0.5 + min(len(word)/10, 0.5)))
                          for word, freq in frequencia.items()]

        # Ordena por score e retorna os top_n
        return sorted(palavras_chave, key=lambda x: x[1], reverse=True)[:top_n]

    def identificar_topicos(self, textos: List[str], num_topicos: int = 5) -> Dict:
        """
        Identifica tópicos emergentes usando agrupamento simples de termos

        Args:
            textos (List[str]): Lista de textos para análise
            num_topicos (int): Número de tópicos para identificar

        Returns:
            Dict: Dicionário com tópicos identificados
        """
        # Pré-processamento
        tokens_por_texto = []
        for texto in textos:
            tokens = self.remover_stopwords(self.tokenizar_texto(texto))
            if tokens:
                tokens_por_texto.append(tokens)

        if not tokens_por_texto:
            return {"topicos": []}

        # Combinação de todos os tokens para extrair os termos mais frequentes
        todos_tokens = [token for sublist in tokens_por_texto for token in sublist]
        freq_dist = FreqDist(todos_tokens)

        # Seleciona os termos mais frequentes como "centroides" de tópicos
        termos_principais = [term for term, _ in freq_dist.most_common(num_topicos)]

        # Para cada termo principal, encontra os termos co-ocorrentes
        topicos = {}
        for i, termo in enumerate(termos_principais):
            # Encontra textos que contêm este termo
            textos_relacionados = []
            for tokens in tokens_por_texto:
                if termo in tokens:
                    textos_relacionados.extend(tokens)

            # Encontra termos relacionados
            if textos_relacionados:
                freq_relacionados = FreqDist(textos_relacionados)
                termos_relacionados = [term for term, _ in freq_relacionados.most_common(7)
                                     if term != termo]
                topicos[f"Tópico {i+1} - {termo}"] = termos_relacionados

        return {"topicos": topicos}

    def processar_texto_completo(self, texto: str) -> Dict:
        """
        Realiza processamento completo do texto

        Args:
            texto (str): Texto para processar

        Returns:
            Dict: Resultados do processamento
        """
        # Tokenização em sentenças
        sentencas = self.tokenizar_sentencas(texto)

        # Tokenização em palavras
        tokens = self.tokenizar_texto(texto)

        # Remoção de stopwords
        tokens_sem_stopwords = self.remover_stopwords(tokens)

        # Stemming
        stems = self.aplicar_stemming(tokens_sem_stopwords)

        # Bigramas
        bigramas = self.extrair_ngrams(tokens_sem_stopwords)

        # Frequência
        frequencias = self.calcular_frequencia(tokens_sem_stopwords)

        # Extração de palavras-chave
        palavras_chave = self.extrair_palavras_chave(texto)

        return {
            'texto_original': texto,
            'numero_sentencas': len(sentencas),
            'numero_tokens': len(tokens),
            'numero_tokens_sem_stopwords': len(tokens_sem_stopwords),
            'tokens': tokens,
            'tokens_sem_stopwords': tokens_sem_stopwords,
            'stems': stems,
            'bigramas': bigramas,
            'frequencias': frequencias,
            'palavras_chave': palavras_chave
        }


class GeradorRelatorios:
    """Classe para geração de relatórios e visualizações"""

    def __init__(self):
        """Inicializa o gerador de relatórios"""
        self.processador_nltk = ProcessadorNLTK()

        # Configurações de estilo
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set(style="whitegrid")

    def gerar_grafico_tipos_emergencia(self, df: pd.DataFrame) -> plt.Figure:
        """
        Gera gráfico de tipos de emergência

        Args:
            df (pd.DataFrame): DataFrame com mensagens processadas

        Returns:
            plt.Figure: Figura do gráfico
        """
        if 'tipo_desastre' not in df.columns:
            raise ValueError("DataFrame não contém coluna 'tipo_desastre'")

        contagem = df['tipo_desastre'].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))
        contagem.plot(kind='bar', ax=ax, color='firebrick')

        ax.set_title('Distribuição de Tipos de Emergência', fontsize=15)
        ax.set_xlabel('Tipo de Emergência', fontsize=12)
        ax.set_ylabel('Quantidade', fontsize=12)
        ax.tick_params(axis='x', rotation=45)

        plt.tight_layout()
        return fig

    def gerar_grafico_sentimento(self, df: pd.DataFrame) -> plt.Figure:
        """
        Gera gráfico de análise de sentimento

        Args:
            df (pd.DataFrame): DataFrame com mensagens processadas

        Returns:
            plt.Figure: Figura do gráfico
        """
        if 'sentimento' not in df.columns:
            raise ValueError("DataFrame não contém coluna 'sentimento'")

        contagem = df['sentimento'].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = {'negativo': 'red', 'neutro': 'gray', 'positivo': 'green'}

        contagem.plot(kind='pie', ax=ax, autopct='%1.1f%%',
                     colors=[colors.get(s, 'blue') for s in contagem.index],
                     shadow=True, startangle=90)

        ax.set_title('Distribuição de Sentimentos', fontsize=15)
        ax.set_ylabel('')

        plt.tight_layout()
        return fig

    def gerar_grafico_urgencia(self, df: pd.DataFrame) -> plt.Figure:
        """
        Gera gráfico de níveis de urgência

        Args:
            df (pd.DataFrame): DataFrame com mensagens processadas

        Returns:
            plt.Figure: Figura do gráfico
        """
        if 'nivel_urgencia' not in df.columns:
            raise ValueError("DataFrame não contém coluna 'nivel_urgencia'")

        contagem = df['nivel_urgencia'].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))
        colors = {'crítica': 'darkred', 'alta': 'red', 'média': 'orange', 'baixa': 'yellow'}

        contagem.plot(kind='barh', ax=ax,
                     color=[colors.get(s, 'gray') for s in contagem.index])

        ax.set_title('Distribuição de Níveis de Urgência', fontsize=15)
        ax.set_xlabel('Quantidade', fontsize=12)
        ax.set_ylabel('Nível de Urgência', fontsize=12)

        # Adiciona valores nas barras
        for i, v in enumerate(contagem):
            ax.text(v + 0.5, i, str(v), va='center')

        plt.tight_layout()
        return fig

    def gerar_grafico_temporal(self, df: pd.DataFrame) -> plt.Figure:
        """
        Gera gráfico temporal de mensagens

        Args:
            df (pd.DataFrame): DataFrame com mensagens processadas

        Returns:
            plt.Figure: Figura do gráfico
        """
        if 'data_criacao' not in df.columns:
            raise ValueError("DataFrame não contém coluna 'data_criacao'")

        # Garante que data_criacao é datetime
        df_temp = df.copy()
        df_temp['data_criacao'] = pd.to_datetime(df_temp['data_criacao'])

        # Agrupa por dia
        df_temp['data'] = df_temp['data_criacao'].dt.date
        contagem_diaria = df_temp.groupby('data').size().reset_index(name='count')

        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(x='data', y='count', data=contagem_diaria, marker='o', ax=ax)

        ax.set_title('Evolução Temporal de Mensagens', fontsize=15)
        ax.set_xlabel('Data', fontsize=12)
        ax.set_ylabel('Quantidade de Mensagens', fontsize=12)

        plt.tight_layout()
        return fig

    def gerar_mapa_calor_palavras(self, df: pd.DataFrame) -> plt.Figure:
        """
        Gera mapa de calor das palavras mais frequentes por tipo de emergência

        Args:
            df (pd.DataFrame): DataFrame com mensagens processadas

        Returns:
            plt.Figure: Figura do mapa de calor
        """
        if 'texto' not in df.columns or 'tipo_desastre' not in df.columns:
            raise ValueError("DataFrame não contém as colunas necessárias")

        # Processamento de texto por tipo de emergência
        tipos = df['tipo_desastre'].unique()
        matriz_freq = []

        # Top 20 palavras no conjunto total
        todos_tokens = []
        for texto in df['texto']:
            tokens = self.processador_nltk.tokenizar_texto(texto)
            tokens = self.processador_nltk.remover_stopwords(tokens)
            todos_tokens.extend(tokens)

        freq_total = self.processador_nltk.calcular_frequencia(todos_tokens, 20)
        top_palavras = list(freq_total.keys())

        # Calcula frequência por tipo
        for tipo in tipos:
            textos_tipo = df[df['tipo_desastre'] == tipo]['texto']
            tokens_tipo = []

            for texto in textos_tipo:
                tokens = self.processador_nltk.tokenizar_texto(texto)
                tokens = self.processador_nltk.remover_stopwords(tokens)
                tokens_tipo.extend(tokens)

            freq_tipo = self.processador_nltk.calcular_frequencia(tokens_tipo, 100)

            # Obtém frequência para as top palavras
            freq_row = [freq_tipo.get(palavra, 0) for palavra in top_palavras]
            matriz_freq.append(freq_row)

        # Cria matriz de frequência
        matriz_freq_df = pd.DataFrame(matriz_freq, index=tipos, columns=top_palavras)

        # Gera mapa de calor
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.heatmap(matriz_freq_df, annot=True, cmap='YlOrRd', ax=ax)

        ax.set_title('Frequência de Palavras por Tipo de Emergência', fontsize=15)
        ax.set_xlabel('Palavras', fontsize=12)
        ax.set_ylabel('Tipo de Emergência', fontsize=12)

        plt.tight_layout()
        return fig

    def gerar_nuvem_palavras(self, df: pd.DataFrame, coluna='texto') -> plt.Figure:
        """
        Gera nuvem de palavras a partir dos textos

        Args:
            df (pd.DataFrame): DataFrame com mensagens
            coluna (str): Nome da coluna com os textos

        Returns:
            plt.Figure: Figura com a nuvem de palavras
        """
        if coluna not in df.columns:
            raise ValueError(f"DataFrame não contém a coluna '{coluna}'")

        # Juntar todos os textos
        texto_completo = ' '.join(df[coluna].fillna('').astype(str))

        # Tokenizar e remover stopwords
        tokens = self.processador_nltk.tokenizar_texto(texto_completo)
        tokens = self.processador_nltk.remover_stopwords(tokens)
        texto_processado = ' '.join(tokens)

        # Configurações de cores para palavras de emergência
        palavras_emergencia = {
            'socorro': '#FF0000',
            'emergência': '#FF0000',
            'urgente': '#FF4500',
            'ajuda': '#FF6347',
            'perigo': '#DC143C',
            'risco': '#B22222',
            'bombeiros': '#0000FF',
            'samu': '#008000',
            'resgate': '#4169E1',
            'evacuação': '#FF8C00',
            'desastre': '#8B0000',
            'catástrofe': '#800000',
            'enchente': '#1E90FF',
            'incêndio': '#FF4500',
            'deslizamento': '#8B4513'
        }

        # Função de cor personalizada
        def cor_personalizada(word, **kwargs):
            return palavras_emergencia.get(word.lower(), '#808080')

        # Gerar nuvem de palavras
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            max_words=100,
            color_func=cor_personalizada,
            stopwords=self.processador_nltk.stopwords
        ).generate(texto_processado)

        # Criar figura
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('Nuvem de Palavras - Mensagens de Emergência', fontsize=16)

        plt.tight_layout()
        return fig

    def gerar_resumo_eventos(self, df: pd.DataFrame) -> str:
        """
        Gera um resumo textual dos eventos de desastres naturais

        Args:
            df (pd.DataFrame): DataFrame com mensagens processadas

        Returns:
            str: Resumo textual formatado dos eventos
        """
        # Verifica se o DataFrame está vazio
        if df.empty:
            return "Nenhum evento registrado no período selecionado."

        # Coleta estatísticas básicas
        total_eventos = len(df)

        # Conta tipos de desastres
        if 'tipo_desastre' in df.columns:
            tipos_contagem = df['tipo_desastre'].value_counts()
            tipos_principais = tipos_contagem.head(3)
            tipos_texto = ", ".join([f"{count} {tipo}" for tipo, count in tipos_principais.items()])
        else:
            tipos_texto = "tipos não classificados"

        # Análise de urgência
        if 'nivel_urgencia' in df.columns:
            urgencia_alta = df[df['nivel_urgencia'] == 'Alto'].shape[0]
            pct_alta_urgencia = (urgencia_alta / total_eventos) * 100 if total_eventos > 0 else 0
        else:
            pct_alta_urgencia = 0

        # Análise de sentimento
        if 'sentimento' in df.columns:
            sentimento_negativo = df[df['sentimento'].isin(['negativo', 'muito negativo'])].shape[0]
            pct_negativo = (sentimento_negativo / total_eventos) * 100 if total_eventos > 0 else 0
        else:
            pct_negativo = 0

        # Análise temporal
        eventos_recentes = ""
        if 'data_criacao' in df.columns or 'data' in df.columns:
            # Usa a coluna 'data' se disponível, senão usa 'data_criacao'
            data_col = 'data' if 'data' in df.columns else 'data_criacao'

            # Converte para datetime se não for
            if not pd.api.types.is_datetime64_any_dtype(df[data_col]):
                df[data_col] = pd.to_datetime(df[data_col], errors='coerce')

            # Verifica se há eventos nas últimas 24 horas
            agora = pd.Timestamp.now()
            eventos_24h = df[df[data_col] > (agora - pd.Timedelta(hours=24))].shape[0]

            if eventos_24h > 0:
                eventos_recentes = f" {eventos_24h} eventos foram registrados nas últimas 24 horas."

        # Localizações mais afetadas
        locais_afetados = ""
        if 'localizacoes' in df.columns and not df['localizacoes'].isna().all():
            # Extrai todos os locais mencionados
            todos_locais = []
            for loc in df['localizacoes']:
                if isinstance(loc, list):
                    for local in loc:
                        if isinstance(local, dict) and 'texto' in local:
                            todos_locais.append(local['texto'])
                elif isinstance(loc, str) and loc:
                    todos_locais.append(loc)

            if todos_locais:
                # Conta frequência e pega os 3 mais comuns
                from collections import Counter
                locais_freq = Counter(todos_locais).most_common(3)
                locais_texto = ", ".join([local for local, _ in locais_freq])
                locais_afetados = f" As regiões mais afetadas são: {locais_texto}."

        # Construção do resumo
        resumo = f"Análise de {total_eventos} eventos de desastres naturais. "
        resumo += f"Os principais tipos de ocorrências são: {tipos_texto}."

        if pct_alta_urgencia > 0:
            resumo += f" {pct_alta_urgencia:.1f}% dos eventos são de alta urgência."

        if pct_negativo > 0:
            resumo += f" {pct_negativo:.1f}% das mensagens têm sentimento negativo."

        resumo += eventos_recentes
        resumo += locais_afetados

        # Extrai palavras-chave dos textos para adicionar contexto
        if 'texto' in df.columns and not df['texto'].isna().all():
            textos = " ".join(df['texto'].dropna().astype(str))
            palavras_chave = self.processador_nltk.extrair_palavras_chave(textos, top_n=5)
            if palavras_chave:
                palavras_texto = ", ".join([palavra for palavra, _ in palavras_chave])
                resumo += f" Palavras-chave nas mensagens: {palavras_texto}."

        return resumo

    def gerar_relatorio_completo(self, df: pd.DataFrame, caminho_saida: str) -> Dict:
        """
        Gera relatório completo de análise

        Args:
            df (pd.DataFrame): DataFrame com mensagens processadas
            caminho_saida (str): Diretório para salvar relatório

        Returns:
            Dict: Estatísticas e caminhos dos arquivos gerados
        """
        os.makedirs(caminho_saida, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Estatísticas gerais
        total_mensagens = len(df)
        periodo = None
        if 'data_criacao' in df.columns:
            df['data_criacao'] = pd.to_datetime(df['data_criacao'])
            min_data = df['data_criacao'].min()
            max_data = df['data_criacao'].max()
            periodo = f"{min_data.strftime('%d/%m/%Y')} a {max_data.strftime('%d/%m/%Y')}"

        # Contagens
        stats = {
            'total_mensagens': total_mensagens,
            'periodo': periodo,
            'por_tipo': df['tipo_desastre'].value_counts().to_dict() if 'tipo_desastre' in df.columns else {},
            'por_urgencia': df['nivel_urgencia'].value_counts().to_dict() if 'nivel_urgencia' in df.columns else {},
            'por_sentimento': df['sentimento'].value_counts().to_dict() if 'sentimento' in df.columns else {}
        }

        # Gerar gráficos
        arquivos = {}

        try:
            # Gráfico de tipos
            fig = self.gerar_grafico_tipos_emergencia(df)
            caminho = os.path.join(caminho_saida, f"tipos_emergencia_{timestamp}.png")
            fig.savefig(caminho)
            arquivos['grafico_tipos'] = caminho
            plt.close(fig)
        except Exception as e:
            logging.error(f"Erro ao gerar gráfico de tipos: {e}")

        try:
            # Gráfico de sentimento
            fig = self.gerar_grafico_sentimento(df)
            caminho = os.path.join(caminho_saida, f"sentimento_{timestamp}.png")
            fig.savefig(caminho)
            arquivos['grafico_sentimento'] = caminho
            plt.close(fig)
        except Exception as e:
            logging.error(f"Erro ao gerar gráfico de sentimento: {e}")

        try:
            # Gráfico de urgência
            fig = self.gerar_grafico_urgencia(df)
            caminho = os.path.join(caminho_saida, f"urgencia_{timestamp}.png")
            fig.savefig(caminho)
            arquivos['grafico_urgencia'] = caminho
            plt.close(fig)
        except Exception as e:
            logging.error(f"Erro ao gerar gráfico de urgência: {e}")

        try:
            # Gráfico temporal
            fig = self.gerar_grafico_temporal(df)
            caminho = os.path.join(caminho_saida, f"temporal_{timestamp}.png")
            fig.savefig(caminho)
            arquivos['grafico_temporal'] = caminho
            plt.close(fig)
        except Exception as e:
            logging.error(f"Erro ao gerar gráfico temporal: {e}")

        try:
            # Nuvem de palavras
            fig = self.gerar_nuvem_palavras(df)
            caminho = os.path.join(caminho_saida, f"nuvem_palavras_{timestamp}.png")
            fig.savefig(caminho)
            arquivos['nuvem_palavras'] = caminho
            plt.close(fig)
        except Exception as e:
            logging.error(f"Erro ao gerar nuvem de palavras: {e}")

        # Salvar estatísticas em JSON
        caminho_json = os.path.join(caminho_saida, f"estatisticas_{timestamp}.json")
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)

        arquivos['estatisticas_json'] = caminho_json

        # Gerar HTML com resultados
        caminho_html = os.path.join(caminho_saida, f"relatorio_{timestamp}.html")

        with open(caminho_html, 'w', encoding='utf-8') as f:
            f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>Relatório de Emergências</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #d9534f; }}
                    h2 {{ color: #f0ad4e; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
                    .stats {{ display: flex; flex-wrap: wrap; }}
                    .stat-box {{ background: #f8f9fa; border-radius: 5px; padding: 15px; margin: 10px; flex: 1; min-width: 200px; box-shadow: 0 0 5px rgba(0,0,0,0.1); }}
                    .stat-number {{ font-size: 24px; font-weight: bold; color: #d9534f; }}
                    .chart {{ margin: 20px 0; text-align: center; }}
                    img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>Relatório de Monitoramento de Emergências</h1>
                <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                <p>Período analisado: {periodo or 'Não especificado'}</p>
                
                <h2>Estatísticas Gerais</h2>
                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-number">{total_mensagens}</div>
                        <div>Total de Mensagens</div>
                    </div>
                </div>
                
                <h2>Visualizações</h2>
                
                <div class="chart">
                    <h3>Distribuição por Tipo de Emergência</h3>
                    <img src="{os.path.basename(arquivos.get('grafico_tipos', ''))}" alt="Tipos de Emergência">
                </div>
                
                <div class="chart">
                    <h3>Distribuição por Nível de Urgência</h3>
                    <img src="{os.path.basename(arquivos.get('grafico_urgencia', ''))}" alt="Níveis de Urgência">
                </div>
                
                <div class="chart">
                    <h3>Distribuição por Sentimento</h3>
                    <img src="{os.path.basename(arquivos.get('grafico_sentimento', ''))}" alt="Sentimentos">
                </div>
                
                <div class="chart">
                    <h3>Evolução Temporal</h3>
                    <img src="{os.path.basename(arquivos.get('grafico_temporal', ''))}" alt="Evolução Temporal">
                </div>
                
                <div class="chart">
                    <h3>Nuvem de Palavras</h3>
                    <img src="{os.path.basename(arquivos.get('nuvem_palavras', ''))}" alt="Nuvem de Palavras">
                </div>
            </body>
            </html>
            """)

        arquivos['relatorio_html'] = caminho_html

        return {
            'estatisticas': stats,
            'arquivos': arquivos
        }


# Funções auxiliares para uso no Streamlit

def figura_para_base64(fig):
    """Converte figura matplotlib para string base64 para exibir no Streamlit"""
    buffer = BytesIO()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode()
    return img_str

def plotly_para_streamlit(df, tipo='urgencia'):
    """Gera gráfico Plotly para uso no Streamlit"""
    if tipo == 'urgencia':
        contagem = df['nivel_urgencia'].value_counts().reset_index()
        contagem.columns = ['Nível de Urgência', 'Quantidade']

        cores = {
            'crítica': '#d9534f',
            'alta': '#f0ad4e',
            'média': '#5bc0de',
            'baixa': '#5cb85c'
        }

        fig = px.bar(
            contagem,
            x='Nível de Urgência',
            y='Quantidade',
            color='Nível de Urgência',
            color_discrete_map=cores,
            title='Distribuição por Nível de Urgência'
        )

    elif tipo == 'tipo':
        contagem = df['tipo_desastre'].value_counts().reset_index()
        contagem.columns = ['Tipo de Desastre', 'Quantidade']

        fig = px.pie(
            contagem,
            values='Quantidade',
            names='Tipo de Desastre',
            title='Distribuição por Tipo de Desastre',
            hole=0.3
        )

    elif tipo == 'sentimento':
        contagem = df['sentimento'].value_counts().reset_index()
        contagem.columns = ['Sentimento', 'Quantidade']

        cores = {
            'positivo': '#5cb85c',
            'neutro': '#f0ad4e',
            'negativo': '#d9534f'
        }

        fig = px.pie(
            contagem,
            values='Quantidade',
            names='Sentimento',
            color='Sentimento',
            color_discrete_map=cores,
            title='Distribuição por Sentimento'
        )

    elif tipo == 'temporal':
        if 'data_criacao' not in df.columns:
            return None

        df_temp = df.copy()
        df_temp['data_criacao'] = pd.to_datetime(df_temp['data_criacao'])
        df_temp['data'] = df_temp['data_criacao'].dt.date
        contagem = df_temp.groupby('data').size().reset_index(name='Quantidade')

        fig = px.line(
            contagem,
            x='data',
            y='Quantidade',
            markers=True,
            title='Evolução Temporal de Mensagens'
        )

    else:
        return None

    fig.update_layout(
        autosize=True,
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig


if __name__ == "__main__":
    # Teste das funcionalidades
    processador = ProcessadorNLTK()
    gerador = GeradorRelatorios()

    print("Módulo de Processamento NLTK e Relatórios carregado com sucesso!")
