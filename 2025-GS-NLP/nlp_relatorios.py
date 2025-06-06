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
import base64  # Adicionando importação do base64
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


def filtrar_por_periodo(df, periodo):
    """
    Filtra o DataFrame pelo período especificado

    Args:
        df (pd.DataFrame): DataFrame a ser filtrado
        periodo (str): Período de filtro ('Últimas 24 horas', 'Última semana', 'Último mês', 'Todo o período')

    Returns:
        pd.DataFrame: DataFrame filtrado
    """
    if periodo == "Todo o período":
        return df

    df = df.copy()
    agora = pd.Timestamp.now()

    # Converte a coluna de data para datetime
    if 'data_criacao' in df.columns:
        df['data_criacao'] = pd.to_datetime(df['data_criacao'], errors='coerce')

    # Define o início do período
    if periodo == "Últimas 24 horas":
        inicio = agora - pd.Timedelta(days=1)
    elif periodo == "Última semana":
        inicio = agora - pd.Timedelta(days=7)
    else:  # Último mês
        inicio = agora - pd.Timedelta(days=30)

    # Aplica o filtro
    df = df[df['data_criacao'].notna()]  # Removes rows with null date
    return df[df['data_criacao'] >= inicio]

class GeradorRelatorios:
    """Classe para geração de relatórios"""

    def __init__(self):
        """Inicializa o gerador de relatórios"""
        self.processador = ProcessadorNLTK()
        self.cores = {
            'critica': '#d9534f',
            'alta': '#f0ad4e',
            'media': '#5bc0de',
            'baixa': '#5cb85c',
            'positivo': '#5cb85c',
            'neutro': '#f0ad4e',
            'negativo': '#d9534f'
        }
        # Definir o caminho base do projeto e do logo
        self.projeto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.logo_path = os.path.join(self.projeto_dir, '2025-GS-NLP', 'FIAP-transparente.png')
        if not os.path.exists(self.logo_path):
            self.logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'FIAP-transparente.png')

    def _copiar_logo(self, diretorio_destino):
        """Copia o logo para o diretório do relatório"""
        try:
            if os.path.exists(self.logo_path):
                logo_destino = os.path.join(diretorio_destino, 'FIAP-transparente.png')
                import shutil
                shutil.copy2(self.logo_path, logo_destino)
                return True
            return False
        except Exception as e:
            logging.error(f"Erro ao copiar logo: {e}")
            return False

    def normalizar_texto(self, texto):
        """Normaliza texto removendo acentos e convertendo para minúsculas"""
        return texto.lower().strip()

    def gerar_grafico_tipos_emergencia(self, df):
        """Gera gráfico de tipos de emergência"""
        plt.figure(figsize=(10, 6))
        if 'tipo_desastre' in df.columns:
            contagem = df['tipo_desastre'].value_counts()
            cores = plt.cm.Set3(np.linspace(0, 1, len(contagem)))
            plt.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=cores)
            plt.title('Distribuição por Tipo de Emergência', pad=20)
        return plt.gcf()

    def gerar_grafico_urgencia(self, df):
        """Gera gráfico de níveis de urgência"""
        plt.figure(figsize=(10, 6))
        if 'nivel_urgencia' in df.columns:
            contagem = df['nivel_urgencia'].value_counts()
            cores = [self.cores.get(self.normalizar_texto(nivel), '#777777') for nivel in contagem.index]
            plt.bar(contagem.index, contagem.values, color=cores)
            plt.title('Distribuição por Nível de Urgência', pad=20)
            plt.ylabel('Quantidade')
            plt.xticks(rotation=45)
            plt.tight_layout()
        return plt.gcf()

    def gerar_grafico_sentimento(self, df):
        """Gera gráfico de sentimentos"""
        plt.figure(figsize=(10, 6))
        if 'sentimento' in df.columns:
            contagem = df['sentimento'].value_counts()
            cores = [self.cores.get(self.normalizar_texto(sent), '#777777') for sent in contagem.index]
            plt.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=cores)
            plt.title('Distribuição por Sentimento', pad=20)
        return plt.gcf()

    def gerar_grafico_temporal(self, df):
        """Gera gráfico temporal"""
        plt.figure(figsize=(12, 6))
        if 'data_criacao' in df.columns:
            df_temp = df.copy()
            df_temp['data'] = pd.to_datetime(df_temp['data_criacao']).dt.date
            contagem = df_temp.groupby('data').size()
            plt.plot(contagem.index, contagem.values, marker='o', color='#e01837')
            plt.title('Evolução Temporal de Mensagens', pad=20)
            plt.xlabel('Data')
            plt.ylabel('Quantidade')
            plt.xticks(rotation=45)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.tight_layout()
        return plt.gcf()

    def gerar_nuvem_palavras(self, df):
        """Gera nuvem de palavras"""
        plt.figure(figsize=(12, 8))
        if 'texto' in df.columns:
            texto_completo = ' '.join(df['texto'].dropna().astype(str))
            tokens = self.processador.tokenizar_texto(texto_completo)
            tokens_limpos = self.processador.remover_stopwords(tokens)
            texto_limpo = ' '.join(tokens_limpos)

            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                colormap='viridis',
                max_words=100,
                collocations=False
            ).generate(texto_limpo)

            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Nuvem de Palavras', pad=20)
            plt.tight_layout()
        return plt.gcf()

    def gerar_relatorio_completo(self, df, diretorio_saida):
        """Gera relatório completo com todas as análises"""
        try:
            # Garante que o diretório existe
            os.makedirs(diretorio_saida, exist_ok=True)

            # Inicializa o timestamp para os nomes dos arquivos
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Processa os dados
            df_processado = filtrar_por_periodo(df, periodo="Todo o período")

            # Copia o logo para o diretório do relatório
            logo_copiado = self._copiar_logo(diretorio_saida)

            # Estatísticas gerais
            total_mensagens = len(df_processado)
            periodo = None
            if 'data_criacao' in df_processado.columns:
                df_processado['data_criacao'] = pd.to_datetime(df_processado['data_criacao'])
                min_data = df_processado['data_criacao'].min()
                max_data = df_processado['data_criacao'].max()
                periodo = f"{min_data.strftime('%d/%m/%Y')} a {max_data.strftime('%d/%m/%Y')}"

            # Contagens e gráficos
            arquivos = {}

            # Gerar e salvar todos os gráficos
            graficos = {
                'grafico_tipos': (self.gerar_grafico_tipos_emergencia, 'tipos_emergencia'),
                'grafico_urgencia': (self.gerar_grafico_urgencia, 'urgencia'),
                'grafico_sentimento': (self.gerar_grafico_sentimento, 'sentimento'),
                'grafico_temporal': (self.gerar_grafico_temporal, 'temporal'),
                'grafico_nuvem': (self.gerar_nuvem_palavras, 'nuvem_palavras')
            }

            # Criar subdiretório para imagens
            img_dir = os.path.join(diretorio_saida, 'img')
            os.makedirs(img_dir, exist_ok=True)

            for key, (func, nome) in graficos.items():
                try:
                    fig = func(df_processado)
                    caminho = os.path.join(img_dir, f"{nome}_{timestamp}.png")
                    fig.savefig(caminho, dpi=300, bbox_inches='tight', pad_inches=0.1)
                    arquivos[key] = caminho
                    plt.close(fig)
                except Exception as e:
                    logging.error(f"Erro ao gerar {nome}: {e}")

            # Estatísticas
            stats = {
                'total_mensagens': total_mensagens,
                'periodo': periodo,
                'por_tipo': df_processado['tipo_desastre'].value_counts().to_dict() if 'tipo_desastre' in df_processado.columns else {},
                'por_urgencia': df_processado['nivel_urgencia'].value_counts().to_dict() if 'nivel_urgencia' in df_processado.columns else {},
                'por_sentimento': df_processado['sentimento'].value_counts().to_dict() if 'sentimento' in df_processado.columns else {}
            }

            # Função auxiliar para obter o caminho relativo das imagens
            def get_img_path(arquivo):
                if arquivo:
                    return os.path.join('img', os.path.basename(arquivo))
                return ''

            # Gerar HTML com resultados
            caminho_html = os.path.join(diretorio_saida, f"relatorio_{timestamp}.html")

            with open(caminho_html, 'w', encoding='utf-8') as f:
                logo_tag = '<img src="FIAP-transparente.png" alt="FIAP Logo" style="max-height: 80px;">' if logo_copiado else ''
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>Relatório de Monitoramento de Emergências</title>
                    <style>
                        body {{
                            font-family: 'Segoe UI', Arial, sans-serif;
                            margin: 0;
                            padding: 0;
                            background-color: #f8f9fa;
                            color: #333;
                        }}
                        .header {{
                            background-color: #fff;
                            padding: 20px;
                            text-align: center;
                            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        }}
                        .header img {{
                            max-height: 80px;
                            margin-bottom: 20px;
                        }}
                        .container {{
                            max-width: 1200px;
                            margin: 0 auto;
                            padding: 20px;
                        }}
                        h1 {{
                            color: #e01837;
                            font-size: 2.5em;
                            margin-bottom: 10px;
                        }}
                        h2 {{
                            color: #1a1a1a;
                            border-bottom: 3px solid #e01837;
                            padding-bottom: 10px;
                            margin-top: 40px;
                        }}
                        h3 {{
                            color: #1a1a1a;
                            margin-top: 0;
                            display: flex;
                            align-items: center;
                            gap: 10px;
                            font-size: 1.2em;
                        }}
                        .stats {{
                            display: flex;
                            flex-wrap: wrap;
                            gap: 20px;
                            margin: 30px 0;
                        }}
                        .stat-box {{
                            background: #fff;
                            border-radius: 10px;
                            padding: 20px;
                            flex: 1;
                            min-width: 250px;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            transition: transform 0.2s;
                        }}
                        .stat-box:hover {{
                            transform: translateY(-5px);
                        }}
                        .stat-number {{
                            font-size: 32px;
                            font-weight: bold;
                            color: #e01837;
                            margin-bottom: 10px;
                        }}
                        .chart {{
                            background: #fff;
                            border-radius: 10px;
                            padding: 20px;
                            margin: 20px 0;
                            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        }}
                        .chart img {{
                            max-width: 100%;
                            height: auto;
                            border-radius: 5px;
                            margin: 15px auto;
                            display: block;
                        }}
                        .meta-info {{
                            background: #fff;
                            padding: 15px;
                            border-radius: 10px;
                            margin: 20px 0;
                            color: #666;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        {logo_tag}
                        <h1>Relatório de Monitoramento de Emergências</h1>
                    </div>
                    
                    <div class="container">
                        <div class="meta-info">
                            <p><strong>Data de Geração:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
                            <p><strong>Período Analisado:</strong> {periodo or 'Não especificado'}</p>
                        </div>
                        
                        <h2>Estatísticas Gerais</h2>
                        <div class="stats">
                            <div class="stat-box">
                                <div class="stat-number">{total_mensagens}</div>
                                <div>Total de Mensagens</div>
                            </div>
                            {"".join([f'''
                            <div class="stat-box">
                                <div class="stat-number">{len(stats.get(key, {}))}</div>
                                <div>Tipos de {key.split('_')[1].title()}</div>
                            </div>
                            ''' for key in ['por_tipo', 'por_urgencia', 'por_sentimento'] if stats.get(key)])}
                        </div>
                        
                        <h2>Visualizações</h2>
                        
                        <div class="chart">
                            <h3>📊 Distribuição por Tipo de Emergência</h3>
                            <img src="{get_img_path(arquivos['grafico_tipos'])}" alt="Tipos de Emergência" class="chart-img">
                        </div>
                        
                        <div class="chart">
                            <h3>🚨 Distribuição por Nível de Urgência</h3>
                            <img src="{get_img_path(arquivos['grafico_urgencia'])}" alt="Níveis de Urgência" class="chart-img">
                        </div>
                        
                        <div class="chart">
                            <h3>😊 Distribuição por Sentimento</h3>
                            <img src="{get_img_path(arquivos['grafico_sentimento'])}" alt="Sentimentos" class="chart-img">
                        </div>
                        
                        <div class="chart">
                            <h3>📈 Evolução Temporal</h3>
                            <img src="{get_img_path(arquivos['grafico_temporal'])}" alt="Evolução Temporal" class="chart-img">
                        </div>
                        
                        <div class="chart">
                            <h3>☁️ Nuvem de Palavras</h3>
                            <img src="{get_img_path(arquivos['grafico_nuvem'])}" alt="Nuvem de Palavras" class="chart-img">
                        </div>
                    </div>
                </body>
                </html>
                """)

            arquivos['relatorio_html'] = caminho_html

            return {
                'estatisticas': stats,
                'arquivos': arquivos
            }
        except Exception as e:
            logging.error(f"Erro ao gerar relatório: {e}")
            raise Exception(f"Erro ao gerar relatório: {str(e)}")

    def gerar_relatorio_resumido(self, df):
        """Gera um relatório resumido com as principais estatísticas e visualizações"""
        try:
            # Processa os dados
            df_processado = filtrar_por_periodo(df, periodo="Todo o período")

            # Estatísticas básicas
            total_mensagens = len(df_processado)
            periodo = None
            if 'data_criacao' in df_processado.columns:
                df_processado['data_criacao'] = pd.to_datetime(df_processado['data_criacao'])
                min_data = df_processado['data_criacao'].min()
                max_data = df_processado['data_criacao'].max()
                periodo = f"{min_data.strftime('%d/%m/%Y')} a {max_data.strftime('%d/%m/%Y')}"

            # Contagens
            stats = {
                'Informações Gerais': {
                    'Total de Mensagens': total_mensagens,
                    'Período Analisado': periodo or 'Não especificado'
                },
                'Distribuição por Tipo': df_processado['tipo_desastre'].value_counts().to_dict() if 'tipo_desastre' in df_processado.columns else {},
                'Distribuição por Urgência': df_processado['nivel_urgencia'].value_counts().to_dict() if 'nivel_urgencia' in df_processado.columns else {},
                'Distribuição por Sentimento': df_processado['sentimento'].value_counts().to_dict() if 'sentimento' in df_processado.columns else {}
            }

            # Gerar visualizações como imagens base64
            visualizacoes = {}

            # Gráfico de tipos
            try:
                fig_tipos = self.gerar_grafico_tipos_emergencia(df_processado)
                visualizacoes['tipos'] = figura_para_base64(fig_tipos)
                plt.close(fig_tipos)
            except Exception as e:
                logging.error(f"Erro ao gerar gráfico de tipos: {e}")

            # Gráfico de urgência
            try:
                fig_urgencia = self.gerar_grafico_urgencia(df_processado)
                visualizacoes['urgencia'] = figura_para_base64(fig_urgencia)
                plt.close(fig_urgencia)
            except Exception as e:
                logging.error(f"Erro ao gerar gráfico de urgência: {e}")

            # Gráfico temporal
            try:
                fig_temporal = self.gerar_grafico_temporal(df_processado)
                visualizacoes['temporal'] = figura_para_base64(fig_temporal)
                plt.close(fig_temporal)
            except Exception as e:
                logging.error(f"Erro ao gerar gráfico temporal: {e}")

            # Gráfico de sentimentos
            try:
                fig_sentimento = self.gerar_grafico_sentimento(df_processado)
                visualizacoes['sentimento'] = figura_para_base64(fig_sentimento)
                plt.close(fig_sentimento)
            except Exception as e:
                logging.error(f"Erro ao gerar gráfico de sentimento: {e}")

            return {
                'estatisticas': stats,
                'visualizacoes': visualizacoes,
                'periodo_analise': periodo
            }

        except Exception as e:
            logging.error(f"Erro ao gerar relatório resumido: {e}")
            raise Exception(f"Erro ao gerar relatório resumido: {str(e)}")


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
