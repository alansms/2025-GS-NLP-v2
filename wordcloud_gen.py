"""
Módulo de Geração de Nuvem de Palavras
Cria visualizações de nuvem de palavras para mensagens de emergência
"""

import re
import numpy as np
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple
from collections import Counter
import base64
from io import BytesIO
import os


class GeradorNuvemPalavras:
    """Classe para geração de nuvens de palavras personalizadas"""
    
    def __init__(self):
        """Inicializa o gerador de nuvem de palavras"""
        
        # Stop words em português (palavras comuns a serem removidas)
        self.stop_words = {
            'a', 'o', 'e', 'é', 'de', 'do', 'da', 'em', 'um', 'uma', 'para',
            'com', 'não', 'na', 'no', 'se', 'que', 'por', 'mais', 'as', 'os',
            'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 'seu', 'sua',
            'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu',
            'também', 'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre',
            'era', 'depois', 'sem', 'mesmo', 'aos', 'ter', 'seus', 'suas',
            'numa', 'pelos', 'pelas', 'esse', 'essa', 'num', 'nem', 'suas',
            'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 'pelas', 'seu',
            'aqui', 'ali', 'lá', 'então', 'agora', 'hoje', 'ontem', 'amanhã',
            'sim', 'não', 'talvez', 'quem', 'onde', 'quando', 'como', 'porque',
            'rt', 'via', 'http', 'https', 'www', 'com', 'br', 'org'
        }
        
        # Palavras específicas de emergência para destacar
        self.palavras_emergencia = {
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
            'deslizamento': '#8B4513',
            'vendaval': '#708090',
            'terremoto': '#A0522D'
        }
        
        # Configurações padrão
        self.config_padrao = {
            'width': 800,
            'height': 400,
            'background_color': 'white',
            'max_words': 100,
            'relative_scaling': 0.5,
            'min_font_size': 10,
            'max_font_size': 100,
            'colormap': 'viridis'
        }
    
    def preprocessar_texto(self, textos: List[str]) -> str:
        """
        Preprocessa lista de textos para nuvem de palavras
        
        Args:
            textos (List[str]): Lista de textos
            
        Returns:
            str: Texto preprocessado concatenado
        """
        texto_completo = ' '.join(textos)
        
        # Remove URLs
        texto_completo = re.sub(r'http\S+|www\S+|https\S+', '', texto_completo, flags=re.MULTILINE)
        
        # Remove menções e hashtags
        texto_completo = re.sub(r'@\w+|#\w+', '', texto_completo)
        
        # Remove números de telefone
        texto_completo = re.sub(r'\b\d{2,5}[-\s]?\d{4,5}[-\s]?\d{4}\b', '', texto_completo)
        
        # Remove caracteres especiais, mantém acentos
        texto_completo = re.sub(r'[^\w\sáàâãéèêíìîóòôõúùûç]', ' ', texto_completo)
        
        # Converte para minúsculas
        texto_completo = texto_completo.lower()
        
        # Remove palavras muito curtas (menos de 3 caracteres)
        palavras = texto_completo.split()
        palavras_filtradas = [palavra for palavra in palavras 
                             if len(palavra) >= 3 and palavra not in self.stop_words]
        
        return ' '.join(palavras_filtradas)
    
    def extrair_palavras_frequentes(self, texto: str, top_n: int = 50) -> Dict[str, int]:
        """
        Extrai palavras mais frequentes do texto
        
        Args:
            texto (str): Texto preprocessado
            top_n (int): Número de palavras mais frequentes
            
        Returns:
            Dict[str, int]: Dicionário palavra -> frequência
        """
        palavras = texto.split()
        contador = Counter(palavras)
        return dict(contador.most_common(top_n))
    
    def criar_funcao_cor_personalizada(self):
        """
        Cria função de cor personalizada para destacar palavras de emergência
        
        Returns:
            function: Função de cor personalizada
        """
        def cor_personalizada(word, font_size, position, orientation, random_state=None, **kwargs):
            # Verifica se é palavra de emergência
            if word.lower() in self.palavras_emergencia:
                return self.palavras_emergencia[word.lower()]
            
            # Cores baseadas na frequência/tamanho da fonte
            if font_size > 60:
                return '#FF0000'  # Vermelho para palavras muito frequentes
            elif font_size > 40:
                return '#FF4500'  # Laranja para palavras frequentes
            elif font_size > 25:
                return '#1E90FF'  # Azul para palavras moderadas
            else:
                return '#808080'  # Cinza para palavras menos frequentes
        
        return cor_personalizada
    
    def gerar_nuvem_palavras(self, textos: List[str], 
                           titulo: str = "Nuvem de Palavras - Emergências",
                           config: Optional[Dict] = None,
                           salvar_arquivo: Optional[str] = None) -> Tuple[plt.Figure, Dict]:
        """
        Gera nuvem de palavras a partir de lista de textos
        
        Args:
            textos (List[str]): Lista de textos
            titulo (str): Título da visualização
            config (Dict, optional): Configurações personalizadas
            salvar_arquivo (str, optional): Caminho para salvar imagem
            
        Returns:
            Tuple[plt.Figure, Dict]: Figura matplotlib e estatísticas
        """
        if not textos:
            raise ValueError("Lista de textos não pode estar vazia")
        
        # Usa configuração padrão se não fornecida
        config_final = {**self.config_padrao, **(config or {})}
        
        # Preprocessa textos
        texto_processado = self.preprocessar_texto(textos)
        
        if not texto_processado.strip():
            raise ValueError("Nenhum texto válido após preprocessamento")
        
        # Extrai palavras frequentes para estatísticas
        palavras_freq = self.extrair_palavras_frequentes(texto_processado)
        
        # Cria WordCloud
        wordcloud = WordCloud(
            width=config_final['width'],
            height=config_final['height'],
            background_color=config_final['background_color'],
            max_words=config_final['max_words'],
            relative_scaling=config_final['relative_scaling'],
            min_font_size=config_final['min_font_size'],
            max_font_size=config_final['max_font_size'],
            color_func=self.criar_funcao_cor_personalizada(),
            font_path=None,  # Usa fonte padrão
            prefer_horizontal=0.7,
            stopwords=self.stop_words
        ).generate(texto_processado)
        
        # Cria figura
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        
        # Adiciona legenda para cores de emergência
        self._adicionar_legenda_cores(fig)
        
        plt.tight_layout()
        
        # Salva arquivo se solicitado
        if salvar_arquivo:
            plt.savefig(salvar_arquivo, dpi=300, bbox_inches='tight')
        
        # Calcula estatísticas
        estatisticas = {
            'total_textos': len(textos),
            'total_palavras_unicas': len(palavras_freq),
            'palavra_mais_frequente': max(palavras_freq.items(), key=lambda x: x[1]) if palavras_freq else None,
            'top_10_palavras': dict(list(palavras_freq.items())[:10]),
            'palavras_emergencia_encontradas': [palavra for palavra in palavras_freq.keys() 
                                              if palavra in self.palavras_emergencia],
            'densidade_emergencia': len([p for p in palavras_freq.keys() 
                                       if p in self.palavras_emergencia]) / len(palavras_freq) if palavras_freq else 0
        }
        
        return fig, estatisticas
    
    def _adicionar_legenda_cores(self, fig):
        """
        Adiciona legenda explicando as cores das palavras
        
        Args:
            fig: Figura matplotlib
        """
        # Cria texto de legenda
        legenda_texto = [
            "Cores das palavras:",
            "■ Vermelho: Emergência crítica",
            "■ Laranja: Alta urgência",
            "■ Azul: Moderada",
            "■ Cinza: Baixa frequência"
        ]
        
        # Adiciona texto no canto inferior direito
        fig.text(0.98, 0.02, '\n'.join(legenda_texto), 
                fontsize=8, ha='right', va='bottom',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgray', alpha=0.7))
    
    def gerar_nuvem_por_categoria(self, dados: pd.DataFrame, 
                                 coluna_texto: str = 'texto',
                                 coluna_categoria: str = 'tipo_desastre',
                                 salvar_diretorio: Optional[str] = None) -> Dict:
        """
        Gera nuvens de palavras separadas por categoria
        
        Args:
            dados (pd.DataFrame): DataFrame com dados
            coluna_texto (str): Nome da coluna com textos
            coluna_categoria (str): Nome da coluna com categorias
            salvar_diretorio (str, optional): Diretório para salvar imagens
            
        Returns:
            Dict: Dicionário com figuras e estatísticas por categoria
        """
        if dados.empty:
            return {}
        
        resultados = {}
        categorias = dados[coluna_categoria].unique()
        
        for categoria in categorias:
            # Filtra dados da categoria
            dados_categoria = dados[dados[coluna_categoria] == categoria]
            textos_categoria = dados_categoria[coluna_texto].tolist()
            
            if not textos_categoria:
                continue
            
            try:
                # Gera nuvem para categoria
                titulo = f"Nuvem de Palavras - {categoria.title()}"
                fig, stats = self.gerar_nuvem_palavras(
                    textos_categoria, 
                    titulo=titulo,
                    salvar_arquivo=f"{salvar_diretorio}/nuvem_{categoria}.png" if salvar_diretorio else None
                )
                
                resultados[categoria] = {
                    'figura': fig,
                    'estatisticas': stats,
                    'total_mensagens': len(textos_categoria)
                }
                
            except Exception as e:
                print(f"Erro ao gerar nuvem para categoria {categoria}: {e}")
                continue
        
        return resultados
    
    def gerar_nuvem_comparativa(self, dados1: List[str], dados2: List[str],
                               labels: Tuple[str, str] = ("Grupo 1", "Grupo 2"),
                               salvar_arquivo: Optional[str] = None) -> plt.Figure:
        """
        Gera nuvem de palavras comparativa entre dois grupos
        
        Args:
            dados1 (List[str]): Textos do primeiro grupo
            dados2 (List[str]): Textos do segundo grupo
            labels (Tuple[str, str]): Rótulos dos grupos
            salvar_arquivo (str, optional): Caminho para salvar
            
        Returns:
            plt.Figure: Figura com comparação
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Gera nuvem para grupo 1
        if dados1:
            texto1 = self.preprocessar_texto(dados1)
            if texto1.strip():
                wc1 = WordCloud(
                    width=400, height=300,
                    background_color='white',
                    color_func=self.criar_funcao_cor_personalizada(),
                    stopwords=self.stop_words
                ).generate(texto1)
                ax1.imshow(wc1, interpolation='bilinear')
            ax1.set_title(f"{labels[0]} ({len(dados1)} mensagens)", fontweight='bold')
            ax1.axis('off')
        
        # Gera nuvem para grupo 2
        if dados2:
            texto2 = self.preprocessar_texto(dados2)
            if texto2.strip():
                wc2 = WordCloud(
                    width=400, height=300,
                    background_color='white',
                    color_func=self.criar_funcao_cor_personalizada(),
                    stopwords=self.stop_words
                ).generate(texto2)
                ax2.imshow(wc2, interpolation='bilinear')
            ax2.set_title(f"{labels[1]} ({len(dados2)} mensagens)", fontweight='bold')
            ax2.axis('off')
        
        plt.tight_layout()
        
        if salvar_arquivo:
            plt.savefig(salvar_arquivo, dpi=300, bbox_inches='tight')
        
        return fig
    
    def converter_figura_base64(self, fig: plt.Figure) -> str:
        """
        Converte figura matplotlib para string base64
        
        Args:
            fig (plt.Figure): Figura matplotlib
            
        Returns:
            str: String base64 da imagem
        """
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        
        # Converte para base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        
        return f"data:image/png;base64,{img_base64}"
    
    def obter_palavras_trending(self, dados_historicos: pd.DataFrame,
                               coluna_texto: str = 'texto',
                               coluna_data: str = 'data_criacao',
                               janela_horas: int = 24) -> Dict:
        """
        Identifica palavras em tendência (trending)
        
        Args:
            dados_historicos (pd.DataFrame): Dados históricos
            coluna_texto (str): Coluna com textos
            coluna_data (str): Coluna com datas
            janela_horas (int): Janela de tempo em horas
            
        Returns:
            Dict: Palavras trending e estatísticas
        """
        if dados_historicos.empty:
            return {}
        
        # Converte datas
        dados_historicos[coluna_data] = pd.to_datetime(dados_historicos[coluna_data])
        
        # Define períodos
        agora = pd.Timestamp.now()
        periodo_atual = agora - pd.Timedelta(hours=janela_horas)
        periodo_anterior = periodo_atual - pd.Timedelta(hours=janela_horas)
        
        # Filtra dados
        dados_atuais = dados_historicos[dados_historicos[coluna_data] >= periodo_atual]
        dados_anteriores = dados_historicos[
            (dados_historicos[coluna_data] >= periodo_anterior) & 
            (dados_historicos[coluna_data] < periodo_atual)
        ]
        
        # Extrai palavras frequentes de cada período
        if not dados_atuais.empty:
            texto_atual = self.preprocessar_texto(dados_atuais[coluna_texto].tolist())
            palavras_atuais = self.extrair_palavras_frequentes(texto_atual)
        else:
            palavras_atuais = {}
        
        if not dados_anteriores.empty:
            texto_anterior = self.preprocessar_texto(dados_anteriores[coluna_texto].tolist())
            palavras_anteriores = self.extrair_palavras_frequentes(texto_anterior)
        else:
            palavras_anteriores = {}
        
        # Calcula trending (palavras que aumentaram de frequência)
        trending = {}
        for palavra, freq_atual in palavras_atuais.items():
            freq_anterior = palavras_anteriores.get(palavra, 0)
            if freq_anterior > 0:
                crescimento = (freq_atual - freq_anterior) / freq_anterior
                if crescimento > 0.5:  # Crescimento de pelo menos 50%
                    trending[palavra] = {
                        'freq_atual': freq_atual,
                        'freq_anterior': freq_anterior,
                        'crescimento_pct': crescimento * 100
                    }
            elif freq_atual >= 3:  # Palavras novas com frequência significativa
                trending[palavra] = {
                    'freq_atual': freq_atual,
                    'freq_anterior': 0,
                    'crescimento_pct': float('inf')
                }
        
        # Ordena por crescimento
        trending_ordenado = dict(sorted(trending.items(), 
                                      key=lambda x: x[1]['crescimento_pct'], 
                                      reverse=True)[:20])
        
        return {
            'palavras_trending': trending_ordenado,
            'periodo_atual': f"{periodo_atual} - {agora}",
            'periodo_anterior': f"{periodo_anterior} - {periodo_atual}",
            'total_mensagens_atual': len(dados_atuais),
            'total_mensagens_anterior': len(dados_anteriores)
        }


# Funções de conveniência
def gerar_nuvem_rapida(textos: List[str], titulo: str = "Nuvem de Palavras") -> plt.Figure:
    """
    Função de conveniência para gerar nuvem rapidamente
    
    Args:
        textos (List[str]): Lista de textos
        titulo (str): Título da nuvem
        
    Returns:
        plt.Figure: Figura da nuvem de palavras
    """
    gerador = GeradorNuvemPalavras()
    fig, _ = gerador.gerar_nuvem_palavras(textos, titulo)
    return fig


if __name__ == "__main__":
    # Teste do módulo
    print("=== Teste do Gerador de Nuvem de Palavras ===")
    
    # Dados de teste
    mensagens_teste = [
        "Socorro! Enchente muito forte na região, água subindo rapidamente",
        "Incêndio de grandes proporções no centro, bombeiros no local",
        "Deslizamento de terra soterrou casas, várias famílias desabrigadas",
        "Vendaval derrubou árvores e postes, falta energia elétrica",
        "Granizo danificou veículos, chuva intensa continua",
        "Emergência médica, pessoa precisando de SAMU urgente",
        "Acidente grave na rodovia, vítimas presas nas ferragens",
        "Evacuação necessária devido ao risco de desabamento",
        "Socorro para idosos ilhados pela enchente",
        "Bombeiros combatendo incêndio florestal há horas"
    ]
    
    try:
        # Teste básico
        gerador = GeradorNuvemPalavras()
        fig, stats = gerador.gerar_nuvem_palavras(
            mensagens_teste, 
            titulo="Teste - Emergências",
            salvar_arquivo="teste_nuvem.png"
        )
        
        print("✓ Nuvem de palavras gerada com sucesso")
        print(f"✓ Total de palavras únicas: {stats['total_palavras_unicas']}")
        print(f"✓ Palavra mais frequente: {stats['palavra_mais_frequente']}")
        print(f"✓ Palavras de emergência encontradas: {stats['palavras_emergencia_encontradas']}")
        print(f"✓ Densidade de emergência: {stats['densidade_emergencia']:.2%}")
        
        # Teste com DataFrame
        df_teste = pd.DataFrame({
            'texto': mensagens_teste,
            'tipo_desastre': ['enchente', 'incendio', 'deslizamento', 'vendaval', 'granizo',
                             'emergencia_medica', 'acidente', 'outros', 'enchente', 'incendio']
        })
        
        nuvens_categoria = gerador.gerar_nuvem_por_categoria(df_teste)
        print(f"✓ Geradas nuvens para {len(nuvens_categoria)} categorias")
        
        # Teste de palavras trending
        df_historico = df_teste.copy()
        df_historico['data_criacao'] = pd.date_range(start='2024-01-01', periods=len(df_teste), freq='H')
        
        trending = gerador.obter_palavras_trending(df_historico)
        print(f"✓ Análise de trending concluída")
        
        plt.close('all')  # Fecha figuras para economizar memória
        
        print("\nTeste concluído com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro no teste: {e}")
        import traceback
        traceback.print_exc()

