"""
Módulo de Classificação de Tipos de Desastre
Utiliza scikit-learn para classificar mensagens por tipo de emergência
"""

import re
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
import joblib
import os


class ClassificadorDesastre:
    """Classe para classificação de tipos de desastre em mensagens emergenciais"""
    
    def __init__(self, modelo_path: Optional[str] = None):
        """
        Inicializa o classificador
        
        Args:
            modelo_path (str, optional): Caminho para modelo pré-treinado
        """
        self.tipos_desastre = [
            'enchente', 'incendio', 'deslizamento', 'vendaval', 'granizo',
            'seca', 'terremoto', 'acidente', 'emergencia_medica', 'outros'
        ]
        
        # Palavras-chave para cada tipo de desastre
        self.palavras_chave = {
            'enchente': [
                'enchente', 'inundação', 'alagamento', 'água', 'chuva', 'rio',
                'córrego', 'transbordou', 'subiu', 'nível', 'represou', 'açude',
                'barragem', 'rompeu', 'vazou', 'molhado', 'submergiu', 'afogando'
            ],
            'incendio': [
                'incêndio', 'fogo', 'queimada', 'chamas', 'fumaça', 'queimando',
                'ardendo', 'combustão', 'brasas', 'cinzas', 'carbonizado',
                'chamuscado', 'arde', 'pegou fogo', 'bombeiros', 'mangueira'
            ],
            'deslizamento': [
                'deslizamento', 'desmoronamento', 'desabamento', 'terra', 'morro',
                'encosta', 'barranco', 'escorregou', 'rolou', 'caiu', 'soterrado',
                'escombros', 'pedras', 'lama', 'erosão', 'rachadura', 'fenda'
            ],
            'vendaval': [
                'vendaval', 'vento', 'ventania', 'rajada', 'tempestade', 'tornado',
                'ciclone', 'furacão', 'tufão', 'derrubou', 'arrancou', 'voou',
                'destelhado', 'quebrou', 'estragou', 'destruiu'
            ],
            'granizo': [
                'granizo', 'pedra de gelo', 'chuva de pedra', 'gelo', 'saraiva',
                'pedrisco', 'bateu', 'machucou', 'quebrou vidro', 'furou',
                'amassou', 'danificou'
            ],
            'seca': [
                'seca', 'estiagem', 'falta de água', 'sem água', 'poço seco',
                'açude vazio', 'rio seco', 'nascente', 'secou', 'racionamento',
                'sede', 'desidratação', 'plantação', 'gado', 'morreu'
            ],
            'terremoto': [
                'terremoto', 'tremor', 'abalo sísmico', 'tremeu', 'balançou',
                'vibrou', 'rachadura', 'fissura', 'prédio', 'estrutura',
                'fundação', 'escala richter'
            ],
            'acidente': [
                'acidente', 'colisão', 'batida', 'capotou', 'atropelamento',
                'explosão', 'vazamento', 'derramamento', 'químico', 'tóxico',
                'gás', 'combustível', 'feridos', 'vítimas', 'ambulância'
            ],
            'emergencia_medica': [
                'emergência médica', 'infarto', 'avc', 'convulsão', 'overdose',
                'envenenamento', 'alergia', 'choque', 'parada cardíaca',
                'respiratória', 'samu', 'uti', 'hospital', 'médico', 'enfermeiro'
            ]
        }
        
        # Pipeline de processamento
        self.pipeline = None
        self.vectorizer = None
        self.modelo = None
        self.treinado = False
        
        # Carrega modelo se fornecido
        if modelo_path and os.path.exists(modelo_path):
            self.carregar_modelo(modelo_path)
    
    def preprocessar_texto(self, texto: str) -> str:
        """
        Preprocessa texto para classificação
        
        Args:
            texto (str): Texto original
            
        Returns:
            str: Texto preprocessado
        """
        # Converte para minúsculas
        texto = texto.lower()
        
        # Remove URLs
        texto = re.sub(r'http\S+|www\S+|https\S+', '', texto, flags=re.MULTILINE)
        
        # Remove menções e hashtags
        texto = re.sub(r'@\w+|#\w+', '', texto)
        
        # Remove números de telefone
        texto = re.sub(r'\b\d{2,5}[-\s]?\d{4,5}[-\s]?\d{4}\b', '', texto)
        
        # Remove caracteres especiais, mantém acentos
        texto = re.sub(r'[^\w\sáàâãéèêíìîóòôõúùûç]', ' ', texto)
        
        # Remove espaços múltiplos
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    def gerar_dados_sinteticos(self) -> pd.DataFrame:
        """
        Gera dados sintéticos para treinamento inicial
        
        Returns:
            pd.DataFrame: Dataset sintético
        """
        dados_sinteticos = []
        
        # Templates de mensagens para cada tipo
        templates = {
            'enchente': [
                "Socorro! A água está subindo muito rápido aqui na {local}",
                "Enchente na região de {local}, várias casas alagadas",
                "Rio transbordou e está inundando tudo por aqui",
                "Chuva forte causou alagamento na {local}",
                "Estamos ilhados pela enchente, precisamos de ajuda"
            ],
            'incendio': [
                "Incêndio de grandes proporções na {local}",
                "Fogo se espalhando rapidamente, muito fumaça",
                "Casa pegando fogo na {local}, bombeiros necessários",
                "Queimada descontrolada ameaça residências",
                "Chamas altas, situação crítica de incêndio"
            ],
            'deslizamento': [
                "Deslizamento de terra na encosta do {local}",
                "Morro desmoronou e soterrou casas",
                "Terra escorregou e bloqueou a estrada",
                "Pessoas soterradas no deslizamento",
                "Barranco caiu sobre as casas"
            ],
            'vendaval': [
                "Vendaval muito forte derrubou árvores",
                "Vento arrancou telhados na {local}",
                "Tempestade com rajadas destruindo tudo",
                "Ventania derrubou postes de energia",
                "Tornado passou pela região"
            ],
            'granizo': [
                "Chuva de granizo está destruindo carros",
                "Pedras de gelo grandes machucando pessoas",
                "Granizo quebrou vidros das casas",
                "Saraiva danificou plantações",
                "Chuva de pedra furou telhados"
            ],
            'acidente': [
                "Acidente grave na {local} com vítimas",
                "Colisão entre veículos, feridos presos",
                "Explosão em posto de combustível",
                "Vazamento de gás tóxico",
                "Atropelamento com vítima grave"
            ],
            'emergencia_medica': [
                "Pessoa passou mal, precisa de SAMU",
                "Infarto, situação crítica médica",
                "Criança com convulsão, urgente",
                "Idoso com AVC, precisa hospital",
                "Overdose, pessoa inconsciente"
            ]
        }
        
        locais = [
            "centro da cidade", "bairro jardim", "vila esperança", "rua principal",
            "avenida central", "distrito industrial", "zona rural", "periferia"
        ]
        
        # Gera mensagens sintéticas
        for tipo, msgs in templates.items():
            for template in msgs:
                for local in locais:
                    # Algumas mensagens com local, outras sem
                    if '{local}' in template:
                        mensagem = template.format(local=local)
                    else:
                        mensagem = template
                    
                    dados_sinteticos.append({
                        'texto': mensagem,
                        'tipo_desastre': tipo
                    })
                
                # Adiciona versão sem local também
                if '{local}' in template:
                    mensagem_sem_local = template.replace(' na {local}', '').replace(' do {local}', '')
                    dados_sinteticos.append({
                        'texto': mensagem_sem_local,
                        'tipo_desastre': tipo
                    })
        
        # Adiciona algumas mensagens de "outros"
        outros_msgs = [
            "Situação estranha acontecendo aqui",
            "Problema não identificado na região",
            "Algo diferente está acontecendo",
            "Situação anômala precisa investigação",
            "Evento não classificado ocorrendo"
        ]
        
        for msg in outros_msgs:
            dados_sinteticos.append({
                'texto': msg,
                'tipo_desastre': 'outros'
            })
        
        return pd.DataFrame(dados_sinteticos)
    
    def treinar_modelo(self, dados: Optional[pd.DataFrame] = None, 
                      algoritmo: str = 'naive_bayes') -> Dict:
        """
        Treina o modelo de classificação
        
        Args:
            dados (pd.DataFrame, optional): Dados de treinamento
            algoritmo (str): Algoritmo a usar ('naive_bayes', 'logistic', 'random_forest')
            
        Returns:
            Dict: Métricas de treinamento
        """
        # Usa dados sintéticos se não fornecidos
        if dados is None:
            dados = self.gerar_dados_sinteticos()
        
        # Preprocessa textos
        dados['texto_processado'] = dados['texto'].apply(self.preprocessar_texto)
        
        # Separa features e target
        X = dados['texto_processado']
        y = dados['tipo_desastre']
        
        # Divide em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Escolhe algoritmo
        if algoritmo == 'naive_bayes':
            modelo = MultinomialNB(alpha=0.1)
        elif algoritmo == 'logistic':
            modelo = LogisticRegression(random_state=42, max_iter=1000)
        elif algoritmo == 'random_forest':
            modelo = RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            raise ValueError(f"Algoritmo {algoritmo} não suportado")
        
        # Cria pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words=None,  # Mantém stop words para português
                min_df=2,
                max_df=0.95
            )),
            ('classifier', modelo)
        ])
        
        # Treina modelo
        self.pipeline.fit(X_train, y_train)
        
        # Avalia modelo
        y_pred = self.pipeline.predict(X_test)
        
        # Cross-validation
        cv_scores = cross_val_score(self.pipeline, X_train, y_train, cv=5)
        
        # Métricas
        metricas = {
            'algoritmo': algoritmo,
            'acuracia_teste': self.pipeline.score(X_test, y_test),
            'acuracia_cv_media': cv_scores.mean(),
            'acuracia_cv_std': cv_scores.std(),
            'total_amostras': len(dados),
            'classes': list(self.pipeline.classes_),
            'relatorio_classificacao': classification_report(y_test, y_pred, output_dict=True)
        }
        
        self.treinado = True
        
        return metricas
    
    def classificar_mensagem(self, texto: str) -> Dict:
        """
        Classifica uma mensagem individual
        
        Args:
            texto (str): Texto da mensagem
            
        Returns:
            Dict: Resultado da classificação
        """
        if not self.treinado:
            # Treina modelo com dados sintéticos se não treinado
            self.treinar_modelo()
        
        texto_processado = self.preprocessar_texto(texto)
        
        # Predição
        predicao = self.pipeline.predict([texto_processado])[0]
        probabilidades = self.pipeline.predict_proba([texto_processado])[0]
        
        # Cria dicionário de probabilidades por classe
        prob_por_classe = dict(zip(self.pipeline.classes_, probabilidades))
        
        # Calcula confiança baseada em palavras-chave
        confianca_palavras = self._calcular_confianca_palavras(texto, predicao)
        
        # Confiança final (média entre probabilidade do modelo e palavras-chave)
        confianca_final = (max(probabilidades) + confianca_palavras) / 2
        
        return {
            'tipo_predito': predicao,
            'confianca': confianca_final,
            'probabilidades': prob_por_classe,
            'confianca_palavras': confianca_palavras,
            'texto_processado': texto_processado
        }
    
    def _calcular_confianca_palavras(self, texto: str, tipo_predito: str) -> float:
        """
        Calcula confiança baseada em palavras-chave específicas
        
        Args:
            texto (str): Texto original
            tipo_predito (str): Tipo predito pelo modelo
            
        Returns:
            float: Score de confiança (0-1)
        """
        if tipo_predito not in self.palavras_chave:
            return 0.5  # Confiança neutra para tipos desconhecidos
        
        texto_lower = texto.lower()
        palavras_tipo = self.palavras_chave[tipo_predito]
        
        # Conta palavras-chave encontradas
        palavras_encontradas = 0
        for palavra in palavras_tipo:
            if palavra in texto_lower:
                palavras_encontradas += 1
        
        # Calcula score (máximo 1.0)
        score = min(palavras_encontradas / len(palavras_tipo) * 2, 1.0)
        
        return score
    
    def classificar_lote(self, mensagens: List[str]) -> pd.DataFrame:
        """
        Classifica um lote de mensagens
        
        Args:
            mensagens (List[str]): Lista de mensagens
            
        Returns:
            pd.DataFrame: DataFrame com classificações
        """
        resultados = []
        
        for i, mensagem in enumerate(mensagens):
            try:
                resultado = self.classificar_mensagem(mensagem)
                resultado['id_mensagem'] = i
                resultado['texto_original'] = mensagem
                resultados.append(resultado)
            except Exception as e:
                print(f"Erro ao classificar mensagem {i}: {e}")
                continue
        
        return pd.DataFrame(resultados)
    
    def salvar_modelo(self, caminho: str):
        """
        Salva o modelo treinado
        
        Args:
            caminho (str): Caminho para salvar o modelo
        """
        if not self.treinado:
            raise ValueError("Modelo não foi treinado ainda")
        
        joblib.dump(self.pipeline, caminho)
        print(f"Modelo salvo em: {caminho}")
    
    def carregar_modelo(self, caminho: str):
        """
        Carrega modelo pré-treinado
        
        Args:
            caminho (str): Caminho do modelo
        """
        self.pipeline = joblib.load(caminho)
        self.treinado = True
        print(f"Modelo carregado de: {caminho}")
    
    def obter_estatisticas_classificacao(self, df_classificacoes: pd.DataFrame) -> Dict:
        """
        Calcula estatísticas das classificações
        
        Args:
            df_classificacoes (pd.DataFrame): DataFrame com classificações
            
        Returns:
            Dict: Estatísticas
        """
        if df_classificacoes.empty:
            return {}
        
        stats = {
            'total_mensagens': len(df_classificacoes),
            'distribuicao_tipos': df_classificacoes['tipo_predito'].value_counts().to_dict(),
            'confianca_media': df_classificacoes['confianca'].mean(),
            'confianca_por_tipo': df_classificacoes.groupby('tipo_predito')['confianca'].mean().to_dict(),
            'mensagens_alta_confianca': len(df_classificacoes[df_classificacoes['confianca'] >= 0.8]),
            'mensagens_baixa_confianca': len(df_classificacoes[df_classificacoes['confianca'] < 0.5])
        }
        
        return stats


# Função de conveniência
def classificar_desastre_rapido(texto: str) -> Dict:
    """
    Função de conveniência para classificação rápida
    
    Args:
        texto (str): Texto para classificação
        
    Returns:
        Dict: Resultado da classificação
    """
    classificador = ClassificadorDesastre()
    return classificador.classificar_mensagem(texto)


if __name__ == "__main__":
    # Teste do módulo
    mensagens_teste = [
        "Socorro! Enchente muito forte aqui na região, água subindo rápido",
        "Incêndio de grandes proporções no centro da cidade, muito fumaça",
        "Deslizamento de terra soterrou várias casas na encosta",
        "Vendaval derrubou árvores e postes na avenida principal",
        "Chuva de granizo está quebrando vidros dos carros",
        "Acidente grave na rodovia com várias vítimas",
        "Pessoa passou mal, precisa de ambulância urgente"
    ]
    
    print("=== Teste do Classificador de Desastres ===")
    
    classificador = ClassificadorDesastre()
    
    # Treina modelo
    print("Treinando modelo...")
    metricas = classificador.treinar_modelo()
    print(f"Modelo treinado com acurácia: {metricas['acuracia_teste']:.3f}")
    print(f"Cross-validation: {metricas['acuracia_cv_media']:.3f} ± {metricas['acuracia_cv_std']:.3f}")
    
    # Testa classificações
    print("\n--- Classificações ---")
    for i, msg in enumerate(mensagens_teste):
        resultado = classificador.classificar_mensagem(msg)
        print(f"\nMensagem {i+1}: {msg}")
        print(f"Tipo: {resultado['tipo_predito']}")
        print(f"Confiança: {resultado['confianca']:.3f}")
        print(f"Top 3 probabilidades:")
        probs_ordenadas = sorted(resultado['probabilidades'].items(), 
                               key=lambda x: x[1], reverse=True)[:3]
        for tipo, prob in probs_ordenadas:
            print(f"  {tipo}: {prob:.3f}")
    
    # Estatísticas em lote
    df_resultados = classificador.classificar_lote(mensagens_teste)
    stats = classificador.obter_estatisticas_classificacao(df_resultados)
    
    print("\n--- Estatísticas Gerais ---")
    print(f"Total de mensagens: {stats['total_mensagens']}")
    print(f"Distribuição de tipos: {stats['distribuicao_tipos']}")
    print(f"Confiança média: {stats['confianca_media']:.3f}")
    print(f"Mensagens alta confiança (≥0.8): {stats['mensagens_alta_confianca']}")
    print(f"Mensagens baixa confiança (<0.5): {stats['mensagens_baixa_confianca']}")

