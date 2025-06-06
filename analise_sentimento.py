"""
Módulo de Análise de Sentimento para Mensagens de Emergência
Suporta TextBlob e VADER para análise de sentimento em português
"""

import re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
from typing import Dict, List, Tuple


class AnalisadorSentimento:
    """Classe para análise de sentimento de mensagens emergenciais"""
    
    def __init__(self, metodo='vader'):
        """
        Inicializa o analisador de sentimento
        
        Args:
            metodo (str): 'vader' ou 'textblob'
        """
        self.metodo = metodo
        if metodo == 'vader':
            self.analyzer = SentimentIntensityAnalyzer()
        
        # Palavras-chave que indicam urgência/emergência
        self.palavras_urgencia = [
            'socorro', 'ajuda', 'emergência', 'urgente', 'perigo', 'risco',
            'desespero', 'preso', 'presa', 'ilhado', 'ilhada', 'não consigo',
            'criança', 'idoso', 'ferido', 'ferida', 'machucado', 'sangue',
            'morrer', 'morrendo', 'afogando', 'sufocando', 'desabou',
            'desmoronou', 'incêndio', 'fogo', 'queimando', 'fumaça'
        ]
        
        # Palavras que intensificam o sentimento negativo
        self.intensificadores = [
            'muito', 'extremamente', 'totalmente', 'completamente',
            'desesperadamente', 'urgentemente', 'rapidamente'
        ]
    
    def preprocessar_texto(self, texto: str) -> str:
        """
        Preprocessa o texto para análise
        
        Args:
            texto (str): Texto original
            
        Returns:
            str: Texto preprocessado
        """
        # Remove URLs
        texto = re.sub(r'http\S+|www\S+|https\S+', '', texto, flags=re.MULTILINE)
        
        # Remove menções e hashtags para análise de sentimento
        texto = re.sub(r'@\w+|#\w+', '', texto)
        
        # Remove caracteres especiais excessivos
        texto = re.sub(r'[^\w\s]', ' ', texto)
        
        # Remove espaços múltiplos
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto.lower()
    
    def analisar_com_vader(self, texto: str) -> Dict:
        """
        Analisa sentimento usando VADER
        
        Args:
            texto (str): Texto para análise
            
        Returns:
            Dict: Scores de sentimento
        """
        scores = self.analyzer.polarity_scores(texto)
        
        # Determina sentimento principal
        if scores['compound'] >= 0.05:
            sentimento = 'positivo'
        elif scores['compound'] <= -0.05:
            sentimento = 'negativo'
        else:
            sentimento = 'neutro'
        
        return {
            'sentimento': sentimento,
            'score_positivo': scores['pos'],
            'score_negativo': scores['neg'],
            'score_neutro': scores['neu'],
            'score_composto': scores['compound'],
            'metodo': 'vader'
        }
    
    def analisar_com_textblob(self, texto: str) -> Dict:
        """
        Analisa sentimento usando TextBlob
        
        Args:
            texto (str): Texto para análise
            
        Returns:
            Dict: Scores de sentimento
        """
        blob = TextBlob(texto)
        polaridade = blob.sentiment.polarity
        subjetividade = blob.sentiment.subjectivity
        
        # Determina sentimento principal
        if polaridade > 0.1:
            sentimento = 'positivo'
        elif polaridade < -0.1:
            sentimento = 'negativo'
        else:
            sentimento = 'neutro'
        
        return {
            'sentimento': sentimento,
            'polaridade': polaridade,
            'subjetividade': subjetividade,
            'score_composto': polaridade,
            'metodo': 'textblob'
        }
    
    def calcular_urgencia(self, texto: str) -> Dict:
        """
        Calcula nível de urgência baseado em palavras-chave
        
        Args:
            texto (str): Texto para análise
            
        Returns:
            Dict: Informações de urgência
        """
        texto_lower = texto.lower()
        
        # Conta palavras de urgência
        palavras_encontradas = []
        for palavra in self.palavras_urgencia:
            if palavra in texto_lower:
                palavras_encontradas.append(palavra)
        
        # Conta intensificadores
        intensificadores_encontrados = []
        for intensificador in self.intensificadores:
            if intensificador in texto_lower:
                intensificadores_encontrados.append(intensificador)
        
        # Calcula score de urgência (0-10)
        score_urgencia = len(palavras_encontradas) * 2 + len(intensificadores_encontrados)
        score_urgencia = min(score_urgencia, 10)  # Máximo 10
        
        # Determina nível de urgência
        if score_urgencia >= 7:
            nivel = 'crítica'
        elif score_urgencia >= 4:
            nivel = 'alta'
        elif score_urgencia >= 2:
            nivel = 'média'
        else:
            nivel = 'baixa'
        
        return {
            'nivel_urgencia': nivel,
            'score_urgencia': score_urgencia,
            'palavras_urgencia': palavras_encontradas,
            'intensificadores': intensificadores_encontrados
        }
    
    def analisar_mensagem(self, texto: str) -> Dict:
        """
        Análise completa de uma mensagem
        
        Args:
            texto (str): Texto da mensagem
            
        Returns:
            Dict: Análise completa
        """
        texto_processado = self.preprocessar_texto(texto)
        
        # Análise de sentimento
        if self.metodo == 'vader':
            resultado_sentimento = self.analisar_com_vader(texto_processado)
        else:
            resultado_sentimento = self.analisar_com_textblob(texto_processado)
        
        # Análise de urgência
        resultado_urgencia = self.calcular_urgencia(texto)
        
        # Combina resultados
        resultado_completo = {
            'texto_original': texto,
            'texto_processado': texto_processado,
            **resultado_sentimento,
            **resultado_urgencia
        }
        
        return resultado_completo
    
    def analisar_lote(self, mensagens: List[str]) -> pd.DataFrame:
        """
        Analisa um lote de mensagens
        
        Args:
            mensagens (List[str]): Lista de mensagens
            
        Returns:
            pd.DataFrame: DataFrame com análises
        """
        resultados = []
        
        for i, mensagem in enumerate(mensagens):
            try:
                resultado = self.analisar_mensagem(mensagem)
                resultado['id_mensagem'] = i
                resultados.append(resultado)
            except Exception as e:
                print(f"Erro ao analisar mensagem {i}: {e}")
                continue
        
        return pd.DataFrame(resultados)
    
    def obter_estatisticas(self, df_analises: pd.DataFrame) -> Dict:
        """
        Calcula estatísticas das análises
        
        Args:
            df_analises (pd.DataFrame): DataFrame com análises
            
        Returns:
            Dict: Estatísticas
        """
        if df_analises.empty:
            return {}
        
        stats = {
            'total_mensagens': len(df_analises),
            'distribuicao_sentimento': df_analises['sentimento'].value_counts().to_dict(),
            'distribuicao_urgencia': df_analises['nivel_urgencia'].value_counts().to_dict(),
            'score_sentimento_medio': df_analises['score_composto'].mean(),
            'score_urgencia_medio': df_analises['score_urgencia'].mean(),
            'mensagens_criticas': len(df_analises[df_analises['nivel_urgencia'] == 'crítica']),
            'palavras_urgencia_mais_comuns': self._palavras_mais_comuns(df_analises, 'palavras_urgencia')
        }
        
        return stats
    
    def _palavras_mais_comuns(self, df: pd.DataFrame, coluna: str) -> Dict:
        """
        Encontra palavras mais comuns em uma coluna de listas
        
        Args:
            df (pd.DataFrame): DataFrame
            coluna (str): Nome da coluna
            
        Returns:
            Dict: Contagem de palavras
        """
        todas_palavras = []
        for lista_palavras in df[coluna]:
            if isinstance(lista_palavras, list):
                todas_palavras.extend(lista_palavras)
        
        from collections import Counter
        return dict(Counter(todas_palavras).most_common(10))


# Função de conveniência para uso direto
def analisar_sentimento_rapido(texto: str, metodo: str = 'vader') -> Dict:
    """
    Função de conveniência para análise rápida
    
    Args:
        texto (str): Texto para análise
        metodo (str): Método de análise ('vader' ou 'textblob')
        
    Returns:
        Dict: Resultado da análise
    """
    analisador = AnalisadorSentimento(metodo=metodo)
    return analisador.analisar_mensagem(texto)


if __name__ == "__main__":
    # Teste do módulo
    mensagens_teste = [
        "Socorro! Estou preso na enchente e não consigo sair!",
        "Incêndio muito grande na região, precisamos de ajuda urgente!",
        "Situação controlada, bombeiros já chegaram no local",
        "Criança perdida na área do deslizamento, alguém viu?",
        "Obrigado a todos que ajudaram na evacuação"
    ]
    
    print("=== Teste do Analisador de Sentimento ===")
    
    # Teste com VADER
    analisador_vader = AnalisadorSentimento(metodo='vader')
    print("\n--- Análises com VADER ---")
    
    for i, msg in enumerate(mensagens_teste):
        resultado = analisador_vader.analisar_mensagem(msg)
        print(f"\nMensagem {i+1}: {msg}")
        print(f"Sentimento: {resultado['sentimento']}")
        print(f"Urgência: {resultado['nivel_urgencia']} (score: {resultado['score_urgencia']})")
        print(f"Palavras de urgência: {resultado['palavras_urgencia']}")
    
    # Análise em lote
    df_resultados = analisador_vader.analisar_lote(mensagens_teste)
    stats = analisador_vader.obter_estatisticas(df_resultados)
    
    print("\n--- Estatísticas Gerais ---")
    print(f"Total de mensagens: {stats['total_mensagens']}")
    print(f"Distribuição de sentimento: {stats['distribuicao_sentimento']}")
    print(f"Distribuição de urgência: {stats['distribuicao_urgencia']}")
    print(f"Score médio de sentimento: {stats['score_sentimento_medio']:.3f}")
    print(f"Score médio de urgência: {stats['score_urgencia_medio']:.3f}")

