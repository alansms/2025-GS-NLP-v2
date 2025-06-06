"""
Módulo de Coleta de Dados via Twitter API
Coleta tweets em tempo real sobre emergências e desastres naturais
"""

import tweepy
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
from dataclasses import dataclass
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import hashlib
import pickle


@dataclass
class ConfigTwitter:
    """Configuração para autenticação Twitter API"""
    bearer_token: str
    api_key: str = ""
    api_secret: str = ""
    access_token: str = ""
    access_token_secret: str = ""


class ColetorTwitter:
    """Classe para coleta de dados do Twitter sobre emergências"""
    
    def __init__(self, config: ConfigTwitter):
        """
        Inicializa o coletor Twitter
        
        Args:
            config (ConfigTwitter): Configuração de autenticação
        """
        self.config = config
        self.client = None
        self.api = None
        
        # Termos de busca para emergências
        self.termos_emergencia = [
            'enchente', 'inundação', 'alagamento', 'incêndio', 'fogo',
            'deslizamento', 'desmoronamento', 'vendaval', 'tempestade',
            'granizo', 'tornado', 'terremoto', 'acidente', 'socorro',
            'emergência', 'urgente', 'bombeiros', 'samu', 'resgate',
            'evacuação', 'desastre', 'catástrofe', 'tragédia'
        ]
        
        # Configuração de logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Inicializa conexão
        self._inicializar_conexao()

        # Configuração de cache
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)

        # Controle de taxa
        self.last_request_time = datetime.now()
        self.request_count = 0
        self.max_requests_per_window = 300  # Máximo de requisições por janela de 15 minutos
        self.request_window = 15 * 60  # 15 minutos em segundos

        # Configurações de modo simulado
        self.modo_simulado = False
        self.arquivo_dados_simulados = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'mensagens_coletadas.json')

    def ativar_modo_simulado(self, ativar: bool = True):
        """
        Ativa ou desativa o modo simulado que usa dados locais em vez da API

        Args:
            ativar (bool): Se deve ativar o modo simulado
        """
        self.modo_simulado = ativar
        self.logger.info(f"Modo simulado {'ativado' if ativar else 'desativado'}")

    def _inicializar_conexao(self):
        """Inicializa conexão com Twitter API"""
        try:
            # Log para debug da configuração (sem expor o token completo)
            token_preview = self.config.bearer_token[:5] + "..." if self.config.bearer_token else "vazio"
            self.logger.info(f"Inicializando conex��o com bearer_token: {token_preview}")

            # Cliente v2 (recomendado)
            self.client = tweepy.Client(
                bearer_token=self.config.bearer_token,
                consumer_key=self.config.api_key,
                consumer_secret=self.config.api_secret,
                access_token=self.config.access_token,
                access_token_secret=self.config.access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Testa conexão com um endpoint que requer apenas Bearer Token
            # O método get_me() requer OAuth 1.0a, não funciona apenas com Bearer Token
            try:
                # Usando um endpoint que funciona com Bearer Token
                resultado = self.client.get_recent_tweets_count("teste", granularity="day")
                self.logger.info("Conexão com Twitter API estabelecida com sucesso")
            except Exception as e:
                self.logger.warning(f"Teste de conexão falhou: {e}")
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Twitter API: {e}")
            self.client = None
    
    def _verificar_limite_taxa(self) -> bool:
        """
        Verifica se o limite de taxa foi atingido

        Returns:
            bool: True se está ok para fazer requisição, False se deve esperar
        """
        agora = datetime.now()
        tempo_decorrido = (agora - self.last_request_time).total_seconds()

        # Reinicia contador se passou a janela de tempo
        if tempo_decorrido > self.request_window:
            self.request_count = 0
            self.last_request_time = agora
            return True

        # Verifica se atingiu o limite
        if self.request_count >= self.max_requests_per_window:
            tempo_espera = self.request_window - tempo_decorrido
            self.logger.warning(f"Limite de taxa atingido. Espere {int(tempo_espera)} segundos.")
            return False

        return True

    def _gerar_chave_cache(self, query: str, max_resultados: int, horas_atras: int) -> str:
        """
        Gera uma chave única para o cache baseada nos parâmetros da consulta

        Args:
            query (str): Query de busca
            max_resultados (int): Número máximo de resultados
            horas_atras (int): Período de busca em horas

        Returns:
            str: Chave de cache MD5
        """
        # Combina parâmetros em uma string
        params_str = f"{query}_{max_resultados}_{horas_atras}"

        # Gera hash MD5
        return hashlib.md5(params_str.encode()).hexdigest()

    def _salvar_cache(self, chave: str, dados: List[Dict]):
        """
        Salva dados no cache

        Args:
            chave (str): Chave do cache
            dados (List[Dict]): Dados a serem armazenados
        """
        caminho_arquivo = os.path.join(self.cache_dir, f"{chave}.pkl")

        try:
            with open(caminho_arquivo, 'wb') as f:
                pickle.dump({
                    'timestamp': datetime.now(),
                    'dados': dados
                }, f)
            self.logger.info(f"Dados salvos em cache: {caminho_arquivo}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar cache: {e}")

    def _carregar_cache(self, chave: str, validade_minutos: int = 30) -> Optional[List[Dict]]:
        """
        Carrega dados do cache se existirem e forem válidos

        Args:
            chave (str): Chave do cache
            validade_minutos (int): Tempo em minutos para considerar o cache válido

        Returns:
            Optional[List[Dict]]: Dados do cache ou None se inválido/inexistente
        """
        caminho_arquivo = os.path.join(self.cache_dir, f"{chave}.pkl")

        if not os.path.exists(caminho_arquivo):
            return None

        try:
            with open(caminho_arquivo, 'rb') as f:
                cache = pickle.load(f)

            # Verifica validade do cache
            if (datetime.now() - cache['timestamp']).total_seconds() > (validade_minutos * 60):
                self.logger.info(f"Cache expirado: {caminho_arquivo}")
                return None

            self.logger.info(f"Usando dados do cache: {caminho_arquivo}")
            return cache['dados']
        except Exception as e:
            self.logger.error(f"Erro ao carregar cache: {e}")
            return None

    def _carregar_dados_simulados(self, max_resultados: int = 100) -> List[Dict]:
        """
        Carrega dados simulados do arquivo JSON

        Args:
            max_resultados (int): Número máximo de resultados a retornar

        Returns:
            List[Dict]: Lista de mensagens simuladas
        """
        try:
            if os.path.exists(self.arquivo_dados_simulados):
                with open(self.arquivo_dados_simulados, 'r', encoding='utf-8') as f:
                    dados = json.load(f)

                # Limita ao número máximo de resultados
                return dados[:max_resultados]
            else:
                self.logger.error(f"Arquivo de dados simulados não encontrado: {self.arquivo_dados_simulados}")
                return []
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados simulados: {e}")
            return []

    def construir_query_busca(self, termos_customizados: Optional[List[str]] = None,
                             incluir_retweets: bool = False,
                             apenas_portugues: bool = True) -> str:
        """
        Constrói query de busca para Twitter API
        
        Args:
            termos_customizados (List[str], optional): Termos específicos de busca
            incluir_retweets (bool): Se deve incluir retweets
            apenas_portugues (bool): Se deve filtrar apenas português
            
        Returns:
            str: Query formatada para Twitter API
        """
        termos = termos_customizados or self.termos_emergencia
        
        # Constrói query com OR entre termos
        query_termos = " OR ".join(f'"{termo}"' for termo in termos)
        
        # Adiciona filtros
        filtros = []
        
        if not incluir_retweets:
            filtros.append("-is:retweet")
        
        if apenas_portugues:
            filtros.append("lang:pt")
        
        # Filtra apenas tweets com localização (quando possível)
        # Removendo filtros que não são mais suportados pela API
        # filtros.append("has:geo OR place_country:BR")
        filtros.append("place:BR")  # Tentativa de usar um operador válido para Brasil

        # Combina query
        query_final = f"({query_termos})"
        if filtros:
            query_final += " " + " ".join(filtros)
        
        return query_final
    
    def buscar_tweets_recentes(self, query: Optional[str] = None,
                              max_resultados: int = 100,
                              horas_atras: int = 24,
                              usar_cache: bool = True) -> List[Dict]:
        """
        Busca tweets recentes sobre emergências
        
        Args:
            query (str, optional): Query customizada
            max_resultados (int): Máximo de tweets a retornar
            horas_atras (int): Quantas horas atrás buscar
            usar_cache (bool): Se deve usar cache para requisições recentes

        Returns:
            List[Dict]: Lista de tweets processados
        """
        # Verifica se deve usar modo simulado
        if self.modo_simulado:
            self.logger.info("Usando dados simulados em vez da API do Twitter")
            return self._carregar_dados_simulados(max_resultados)

        if not self.client:
            self.logger.error("Cliente Twitter não inicializado")
            return []
        
        if not query:
            query = self.construir_query_busca()
        
        # Verifica cache se habilitado
        if usar_cache:
            chave_cache = self._gerar_chave_cache(query, max_resultados, horas_atras)
            dados_cache = self._carregar_cache(chave_cache)
            if dados_cache:
                return dados_cache

        # Calcula data de início
        data_inicio = datetime.utcnow() - timedelta(hours=horas_atras)
        
        tweets_coletados = []
        
        # Impõe limite de solicitações mais conservador
        # Twitter limita a 450 solicitações por 15 minutos para a pesquisa
        # Vamos ser mais conservadores e limitar a 100 solicitações por execução
        max_requests = 10
        requests_count = 0
        max_per_request = min(max_resultados, 10)  # Limitamos a 10 por requisição

        try:
            self.logger.info(f"Buscando tweets com limite conservador de {max_requests} requisições")

            # Busca tweets com limite
            tweets = tweepy.Paginator(
                self.client.search_recent_tweets,
                query=query,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 
                             'context_annotations', 'geo', 'lang'],
                user_fields=['name', 'username', 'location', 'verified'],
                place_fields=['full_name', 'country', 'place_type'],
                expansions=['author_id', 'geo.place_id'],
                start_time=data_inicio,
                max_results=max_per_request  # Limitado a 10 por requisição
            )

            # Controla o número de requisições
            for page in tweets:
                # Verifica limite de taxa antes de cada requisição
                if not self._verificar_limite_taxa():
                    tempo_espera = self.request_window - (datetime.now() - self.last_request_time).total_seconds()
                    self.logger.warning(f"Aguardando {int(tempo_espera)} segundos antes da próxima requisição")
                    time.sleep(min(60, max(1, tempo_espera)))  # Espera no máximo 60 segundos

                requests_count += 1
                self.request_count += 1
                self.last_request_time = datetime.now()

                if page.data:
                    for tweet in page.data:
                        tweet_processado = self._processar_tweet(tweet)
                        if tweet_processado:
                            tweets_coletados.append(tweet_processado)

                # Verifica se atingiu limite de tweets ou requisições
                if len(tweets_coletados) >= max_resultados or requests_count >= max_requests:
                    self.logger.info(f"Limite atingido: {requests_count} requisições, {len(tweets_coletados)} tweets")
                    break

                # Pausa entre requisições para evitar rate limit
                time.sleep(2)  # Pausa de 2 segundos entre requisições

            self.logger.info(f"Coletados {len(tweets_coletados)} tweets em {requests_count} requisições")

            # Salva em cache se habilitado
            if usar_cache:
                chave_cache = self._gerar_chave_cache(query, max_resultados, horas_atras)
                self._salvar_cache(chave_cache, tweets_coletados)

        except tweepy.TooManyRequests:
            self.logger.warning("Rate limit atingido. Ativando modo simulado automaticamente.")
            # Ativa o modo simulado automaticamente
            self.ativar_modo_simulado(True)
            # Retorna dados simulados em vez de esperar
            return self._carregar_dados_simulados(max_resultados)
        except Exception as e:
            self.logger.error(f"Erro ao buscar tweets: {e}")
            # Se houver qualquer erro na API, ativamos o modo simulado como fallback
            self.logger.warning("Ativando modo simulado devido a erro na API.")
            self.ativar_modo_simulado(True)
            return self._carregar_dados_simulados(max_resultados)

        return tweets_coletados
    
    def _processar_tweet(self, tweet) -> Optional[Dict]:
        """
        Processa um tweet individual
        
        Args:
            tweet: Objeto tweet do Tweepy
            
        Returns:
            Dict: Tweet processado ou None se inválido
        """
        try:
            # Extrai informações básicas
            tweet_data = {
                'id': tweet.id,
                'texto': tweet.text,
                'data_criacao': tweet.created_at.isoformat() if tweet.created_at else None,
                'autor_id': tweet.author_id,
                'idioma': getattr(tweet, 'lang', 'pt'),
                'metricas': {
                    'retweets': tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                    'likes': tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                    'replies': tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
                    'quotes': tweet.public_metrics.get('quote_count', 0) if tweet.public_metrics else 0
                },
                'localizacao': None,
                'url': f"https://twitter.com/twitter/status/{tweet.id}",
                'contexto': [],
                'fonte': 'twitter',
                'coletado_em': datetime.utcnow().isoformat()
            }
            
            # Extrai localização se disponível
            if hasattr(tweet, 'geo') and tweet.geo:
                tweet_data['localizacao'] = {
                    'place_id': tweet.geo.get('place_id'),
                    'coordenadas': tweet.geo.get('coordinates')
                }
            
            # Extrai contexto/anotações
            if hasattr(tweet, 'context_annotations') and tweet.context_annotations:
                for annotation in tweet.context_annotations:
                    tweet_data['contexto'].append({
                        'dominio': annotation.get('domain', {}).get('name'),
                        'entidade': annotation.get('entity', {}).get('name'
                        )
                    })
            
            return tweet_data
            
        except Exception as e:
            self.logger.error(f"Erro ao processar tweet {tweet.id}: {e}")
            return None
    
    def coletar_stream_tempo_real(self, callback_funcao, 
                                 termos_customizados: Optional[List[str]] = None,
                                 duracao_minutos: int = 60):
        """
        Coleta tweets em tempo real via streaming
        
        Args:
            callback_funcao: Função para processar cada tweet
            termos_customizados (List[str], optional): Termos específicos
            duracao_minutos (int): Duração da coleta em minutos
        """
        if not self.client:
            self.logger.error("Cliente Twitter não inicializado")
            return
        
        termos = termos_customizados or self.termos_emergencia
        
        class StreamListener(tweepy.StreamingClient):
            def __init__(self, bearer_token, callback, logger):
                super().__init__(bearer_token, wait_on_rate_limit=True)
                self.callback = callback
                self.logger = logger
                self.contador = 0
            
            def on_tweet(self, tweet):
                try:
                    tweet_processado = self._processar_tweet_stream(tweet)
                    if tweet_processado:
                        self.callback(tweet_processado)
                        self.contador += 1
                        if self.contador % 10 == 0:
                            self.logger.info(f"Processados {self.contador} tweets via stream")
                except Exception as e:
                    self.logger.error(f"Erro no stream: {e}")
            
            def _processar_tweet_stream(self, tweet):
                # Processamento similar ao método _processar_tweet
                return {
                    'id': tweet.id,
                    'texto': tweet.text,
                    'data_criacao': datetime.utcnow().isoformat(),
                    'fonte': 'twitter_stream',
                    'coletado_em': datetime.utcnow().isoformat()
                }
        
        try:
            # Cria stream
            stream = StreamListener(self.config.bearer_token, callback_funcao, self.logger)
            
            # Adiciona regras de filtro
            for termo in termos:
                stream.add_rules(tweepy.StreamRule(f'"{termo}" lang:pt -is:retweet'))
            
            self.logger.info(f"Iniciando stream por {duracao_minutos} minutos...")
            
            # Inicia stream com timeout
            stream.filter(threaded=True)
            time.sleep(duracao_minutos * 60)
            stream.disconnect()
            
        except Exception as e:
            self.logger.error(f"Erro no streaming: {e}")
    
    def salvar_dados(self, tweets: List[Dict], arquivo: str):
        """
        Salva tweets coletados em arquivo JSON
        
        Args:
            tweets (List[Dict]): Lista de tweets
            arquivo (str): Caminho do arquivo
        """
        try:
            # Carrega dados existentes se arquivo existe
            dados_existentes = []
            if os.path.exists(arquivo):
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados_json = json.load(f)
                    dados_existentes = dados_json.get('mensagens', [])
            
            # Adiciona novos tweets (evita duplicatas)
            ids_existentes = {tweet['id'] for tweet in dados_existentes}
            novos_tweets = [tweet for tweet in tweets if tweet['id'] not in ids_existentes]
            
            # Atualiza dados
            dados_atualizados = {
                'mensagens': dados_existentes + novos_tweets,
                'ultima_atualizacao': datetime.utcnow().isoformat(),
                'total_coletadas': len(dados_existentes) + len(novos_tweets),
                'estatisticas': self._calcular_estatisticas(dados_existentes + novos_tweets)
            }
            
            # Salva arquivo
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados_atualizados, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Salvos {len(novos_tweets)} novos tweets em {arquivo}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados: {e}")
    
    def _calcular_estatisticas(self, tweets: List[Dict]) -> Dict:
        """
        Calcula estatísticas dos tweets coletados
        
        Args:
            tweets (List[Dict]): Lista de tweets
            
        Returns:
            Dict: Estatísticas
        """
        if not tweets:
            return {}
        
        # Contadores
        por_fonte = {}
        por_hora = {}
        total_engajamento = 0
        
        for tweet in tweets:
            # Por fonte
            fonte = tweet.get('fonte', 'desconhecido')
            por_fonte[fonte] = por_fonte.get(fonte, 0) + 1
            
            # Por hora
            if tweet.get('data_criacao'):
                try:
                    data = datetime.fromisoformat(tweet['data_criacao'].replace('Z', '+00:00'))
                    hora = data.strftime('%Y-%m-%d %H:00')
                    por_hora[hora] = por_hora.get(hora, 0) + 1
                except:
                    pass
            
            # Engajamento
            metricas = tweet.get('metricas', {})
            total_engajamento += sum(metricas.values())
        
        return {
            'total_tweets': len(tweets),
            'por_fonte': por_fonte,
            'por_hora': dict(sorted(por_hora.items())[-24:]),  # Últimas 24 horas
            'engajamento_total': total_engajamento,
            'engajamento_medio': total_engajamento / len(tweets) if tweets else 0
        }

    def buscar_mensagens(self, termos_customizados: Optional[List[str]] = None,
                        max_resultados: int = 100,
                        horas_atras: int = 24) -> List[Dict]:
        """
        Alias para buscar_tweets_recentes

        Args:
            termos_customizados (List[str], optional): Termos específicos de busca
            max_resultados (int): Máximo de tweets a retornar
            horas_atras (int): Quantas horas atrás buscar

        Returns:
            List[Dict]: Lista de tweets processados
        """
        if termos_customizados:
            query = self.construir_query_busca(termos_customizados)
            return self.buscar_tweets_recentes(query=query, max_resultados=max_resultados, horas_atras=horas_atras)
        else:
            return self.buscar_tweets_recentes(max_resultados=max_resultados, horas_atras=horas_atras)


class ColetorAlternativo:
    """Coletor alternativo para quando Twitter API não está disponível"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # URLs de feeds RSS de emergência (exemplos)
        self.feeds_emergencia = [
            'https://www.defesacivil.gov.br/rss',  # Exemplo
            'https://www.bombeiros.gov.br/rss',    # Exemplo
        ]
    
    def gerar_dados_simulados(self, quantidade: int = 50) -> List[Dict]:
        """
        Gera dados simulados para demonstração
        
        Args:
            quantidade (int): Quantidade de mensagens a gerar
            
        Returns:
            List[Dict]: Lista de mensagens simuladas
        """
        import random
        
        templates = [
            "Enchente na região de {local}, água subindo rapidamente",
            "Incêndio de grandes proporções em {local}, bombeiros no local",
            "Deslizamento de terra em {local}, várias famílias desabrigadas",
            "Vendaval derrubou árvores em {local}, trânsito interrompido",
            "Granizo danificou veículos em {local}, chuva intensa",
            "Acidente grave na {local}, vítimas sendo socorridas",
            "Falta de energia em {local} após temporal",
            "Alagamento na {local}, carros presos na água"
        ]
        
        locais = [
            "Zona Sul de São Paulo", "Centro do Rio de Janeiro", "Belo Horizonte",
            "Região Metropolitana de Salvador", "Grande Recife", "Porto Alegre",
            "Curitiba", "Brasília", "Fortaleza", "Manaus", "Goiânia", "Belém"
        ]
        
        mensagens = []
        
        for i in range(quantidade):
            template = random.choice(templates)
            local = random.choice(locais)
            
            # Simula dados de tweet
            mensagem = {
                'id': f'sim_{i}_{int(time.time())}',
                'texto': template.format(local=local),
                'data_criacao': (datetime.utcnow() - timedelta(
                    minutes=random.randint(1, 1440)
                )).isoformat(),
                'autor_id': f'user_{random.randint(1000, 9999)}',
                'idioma': 'pt',
                'metricas': {
                    'retweets': random.randint(0, 50),
                    'likes': random.randint(0, 100),
                    'replies': random.randint(0, 20),
                    'quotes': random.randint(0, 10)
                },
                'localizacao': {
                    'nome': local,
                    'coordenadas': None
                },
                'fonte': 'simulado',
                'coletado_em': datetime.utcnow().isoformat()
            }
            
            mensagens.append(mensagem)
        
        self.logger.info(f"Geradas {len(mensagens)} mensagens simuladas")
        return mensagens


# Funções de conveniência
def criar_coletor_twitter(bearer_token: str, **kwargs) -> ColetorTwitter:
    """
    Cria coletor Twitter com configuração mínima
    
    Args:
        bearer_token (str): Token de autenticação
        **kwargs: Outros parâmetros de configuração
        
    Returns:
        ColetorTwitter: Instância do coletor
    """
    config = ConfigTwitter(bearer_token=bearer_token, **kwargs)
    return ColetorTwitter(config)


def coletar_dados_emergencia(arquivo_saida: str, 
                           config_twitter: Optional[ConfigTwitter] = None,
                           usar_simulacao: bool = True,
                           max_tweets: int = 100) -> Dict:
    """
    Função principal para coleta de dados de emergência
    
    Args:
        arquivo_saida (str): Arquivo para salvar dados
        config_twitter (ConfigTwitter, optional): Configuração Twitter
        usar_simulacao (bool): Se deve usar dados simulados
        max_tweets (int): Máximo de tweets a coletar
        
    Returns:
        Dict: Resultado da coleta
    """
    tweets_coletados = []
    
    # Tenta coletar do Twitter se configurado
    if config_twitter and config_twitter.bearer_token:
        try:
            coletor = ColetorTwitter(config_twitter)
            tweets_coletados = coletor.buscar_tweets_recentes(max_resultados=max_tweets)
        except Exception as e:
            logging.error(f"Erro na coleta Twitter: {e}")
    
    # Usa simulação se necessário ou solicitado
    if not tweets_coletados or usar_simulacao:
        coletor_alt = ColetorAlternativo()
        tweets_simulados = coletor_alt.gerar_dados_simulados(max_tweets)
        tweets_coletados.extend(tweets_simulados)
    
    # Salva dados
    if tweets_coletados:
        # Simula salvamento (para demonstração)
        dados_finais = {
            'mensagens': tweets_coletados,
            'ultima_atualizacao': datetime.utcnow().isoformat(),
            'total_coletadas': len(tweets_coletados),
            'estatisticas': {
                'por_fonte': {'twitter': len([t for t in tweets_coletados if t['fonte'] == 'twitter']),
                             'simulado': len([t for t in tweets_coletados if t['fonte'] == 'simulado'])},
                'total_engajamento': sum(sum(t.get('metricas', {}).values()) for t in tweets_coletados)
            }
        }
        
        with open(arquivo_saida, 'w', encoding='utf-8') as f:
            json.dump(dados_finais, f, ensure_ascii=False, indent=2)
    
    return {
        'sucesso': len(tweets_coletados) > 0,
        'total_coletado': len(tweets_coletados),
        'arquivo': arquivo_saida
    }


if __name__ == "__main__":
    # Teste do módulo
    print("=== Teste do Coletor de Dados ===")
    
    # Teste com dados simulados
    print("\n--- Testando coleta simulada ---")
    resultado = coletar_dados_emergencia(
        arquivo_saida='teste_coleta.json',
        usar_simulacao=True,
        max_tweets=20
    )
    
    print(f"Sucesso: {resultado['sucesso']}")
    print(f"Total coletado: {resultado['total_coletado']}")
    print(f"Arquivo: {resultado['arquivo']}")
    
    # Mostra algumas mensagens
    if os.path.exists('teste_coleta.json'):
        with open('teste_coleta.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
            print(f"\nPrimeiras 3 mensagens coletadas:")
            for i, msg in enumerate(dados['mensagens'][:3]):
                print(f"{i+1}. {msg['texto']}")
                print(f"   Fonte: {msg['fonte']}, Data: {msg['data_criacao']}")
    
    print("\nTeste concluído!")
