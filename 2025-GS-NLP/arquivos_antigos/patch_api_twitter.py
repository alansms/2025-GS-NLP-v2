"""
Patch manual para corrigir o problema da API do Twitter
"""

import streamlit as st
from coleta_twitter_api import ConfigTwitter
from config_manager import salvar_config_twitter, carregar_config_twitter

# Carregar configurações salvas
config_salva = carregar_config_twitter()

if config_salva:
    st.sidebar.success("✅ Configurações da API do Twitter carregadas do arquivo salvo!")
    
    # Usar as configurações salvas
    config_twitter = ConfigTwitter(
        bearer_token=config_salva.get('bearer_token', ''),
        api_key='',
        api_secret='',
        access_token='',
        access_token_secret=''
    )
    
    # Disponibilizar para o aplicativo
    st.session_state.config_twitter = config_twitter

# Interface para configurar API do Twitter
st.sidebar.subheader("🐦 Configurar API do Twitter")
with st.sidebar.expander("Configuração da API", expanded=not config_salva):
    bearer_token = st.text_input(
        "Bearer Token (Obrigatório)",
        type="password",
        value=config_salva.get('bearer_token', '') if config_salva else ""
    )
    
    if st.button("Salvar configurações"):
        if bearer_token:
            # Criar configuração
            config_twitter = ConfigTwitter(
                bearer_token=bearer_token,
                api_key='',
                api_secret='',
                access_token='',
                access_token_secret=''
            )
            
            # Salvar na sessão
            st.session_state.config_twitter = config_twitter
            
            # Salvar em arquivo
            config_dict = {
                'bearer_token': bearer_token,
                'api_key': '',
                'api_secret': '',
                'access_token': '',
                'access_token_secret': ''
            }
            
            if salvar_config_twitter(config_dict):
                st.success("✅ Configurações salvas com sucesso! Não será necessário digitá-las novamente.")
            else:
                st.warning("⚠️ Configurações aplicadas, mas não foi possível salvá-las permanentemente.")
        else:
            st.error("❌ O Bearer Token é obrigatório para a API v2 do Twitter.")
