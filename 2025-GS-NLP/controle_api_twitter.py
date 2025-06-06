"""
Módulo de Controle de API Twitter
Implementa proteções contra rate limit e gerenciamento de modo simulado
"""

import streamlit as st
import os
import json
import logging
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional, Any
import pandas as pd

# Configura logger
logger = logging.getLogger(__name__)

class ControladorAPI:
    """Classe para controle de acesso à API do Twitter"""

    def __init__(self):
        """Inicializa o controlador de API"""
        # Inicializa variáveis de estado na sessão do Streamlit
        if 'modo_simulado' not in st.session_state:
            st.session_state.modo_simulado = True

        if 'config_cache' not in st.session_state:
            st.session_state.config_cache = {
                "usar_cache": True,
                "validade_cache": 30,  # minutos
                "max_requisicoes": 10
            }

        if 'ultima_requisicao' not in st.session_state:
            st.session_state.ultima_requisicao = datetime.now() - timedelta(hours=1)

        if 'contador_requisicoes' not in st.session_state:
            st.session_state.contador_requisicoes = 0

        # Diretório para cache
        self.cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    def mostrar_configuracoes_api(self):
        """Exibe opções de configuração de proteção contra rate limit"""
        st.subheader("🛡️ Proteção contra Rate Limit")

        # Opção para usar dados simulados ou reais
        modo_simulado = st.checkbox(
            "Usar dados simulados (evita rate limit)",
            value=st.session_state.modo_simulado,
            help="Ative esta opção para usar dados simulados em vez de consultar a API do Twitter e evitar problemas de rate limit."
        )

        # Atualiza o estado da sessão
        st.session_state.modo_simulado = modo_simulado

        # Configurações avançadas de cache
        with st.expander("Configurações avançadas de cache"):
            usar_cache = st.checkbox(
                "Usar cache para consultas recentes",
                value=st.session_state.config_cache["usar_cache"],
                help="Armazena resultados de consultas recentes para reduzir chamadas à API"
            )

            validade_cache = st.slider(
                "Validade do cache (minutos)",
                min_value=5,
                max_value=120,
                value=st.session_state.config_cache["validade_cache"],
                step=5,
                help="Tempo em minutos para considerar o cache válido"
            )

            max_requisicoes = st.slider(
                "Máximo de requisições por coleta",
                min_value=1,
                max_value=20,
                value=st.session_state.config_cache["max_requisicoes"],
                help="Limite conservador para evitar atingir o rate limit da API"
            )

            # Armazena as configurações na sessão
            st.session_state.config_cache = {
                "usar_cache": usar_cache,
                "validade_cache": validade_cache,
                "max_requisicoes": max_requisicoes
            }

        # Status atual do controle de taxa
        st.markdown("#### Status atual:")
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Modo de dados",
                "Simulado" if st.session_state.modo_simulado else "Real",
                delta="Seguro" if st.session_state.modo_simulado else "Atenção"
            )

        with col2:
            # Calcula tempo desde a última requisição
            tempo_decorrido = (datetime.now() - st.session_state.ultima_requisicao).total_seconds() / 60
            st.metric(
                "Requisições recentes",
                f"{st.session_state.contador_requisicoes}/450",
                delta=f"há {tempo_decorrido:.1f} min"
            )

        # Mostra alerta se estiver próximo do limite
        if st.session_state.contador_requisicoes > 300 and not st.session_state.modo_simulado:
            st.warning("⚠️ Você está se aproximando do limite de requisições da API do Twitter. Considere ativar o modo simulado.")

    def verificar_limite_requisicoes(self) -> bool:
        """
        Verifica se o limite de requisições foi atingido

        Returns:
            bool: True se pode fazer mais requisições, False se deve aguardar
        """
        # Se modo simulado está ativado, sempre permite
        if st.session_state.modo_simulado:
            return True

        # Verifica janela de 15 minutos
        agora = datetime.now()
        tempo_decorrido = (agora - st.session_state.ultima_requisicao).total_seconds()

        # Se passou mais de 15 minutos, reinicia contador
        if tempo_decorrido > (15 * 60):  # 15 minutos em segundos
            st.session_state.contador_requisicoes = 0
            st.session_state.ultima_requisicao = agora
            return True

        # Verifica se já atingiu o limite configurado
        if st.session_state.contador_requisicoes >= st.session_state.config_cache["max_requisicoes"]:
            tempo_espera = (15 * 60) - tempo_decorrido
            logger.warning(f"Limite de requisições atingido. Aguarde {tempo_espera/60:.1f} minutos.")
            return False

        return True

    def registrar_requisicao(self):
        """Registra uma nova requisição à API"""
        st.session_state.contador_requisicoes += 1
        st.session_state.ultima_requisicao = datetime.now()

    def configurar_coletor_twitter(self, coletor):
        """
        Configura o coletor do Twitter com as opções de proteção

        Args:
            coletor: Instância do ColetorTwitter
        """
        # Configura modo simulado
        coletor.ativar_modo_simulado(st.session_state.modo_simulado)

        # Passa configurações de cache e limite de requisições
        return {
            "usar_cache": st.session_state.config_cache["usar_cache"],
            "max_requisicoes": st.session_state.config_cache["max_requisicoes"],
            "validade_cache": st.session_state.config_cache["validade_cache"]
        }

# Função para integrar o controlador ao app principal
def integrar_controlador_app(app, sidebar=True):
    """
    Integra o controlador ao aplicativo principal

    Args:
        app: Instância do aplicativo principal
        sidebar (bool): Se deve mostrar controles na barra lateral
    """
    controlador = ControladorAPI()

    if sidebar:
        with st.sidebar:
            with st.expander("🛡️ Proteção contra Rate Limit", expanded=True):
                controlador.mostrar_configuracoes_api()
    else:
        controlador.mostrar_configuracoes_api()

    return controlador
