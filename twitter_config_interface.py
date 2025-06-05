"""
Módulo para adicionar o campo Bearer Token na interface do Twitter API
Substitui os campos desnecessários
"""

import streamlit as st
import os
import json

def mostrar_campo_bearer_token():
    """
    Exibe apenas o campo de Bearer Token na interface e oculta os outros campos desnecessários
    """
    # Verifica se existe configuração salva
    config_salva = None
    config_path = os.path.join('config', 'twitter_config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_salva = json.load(f)
        except Exception:
            pass

    # Interface simplificada apenas com Bearer Token
    with st.expander("Configurar API do Twitter", expanded=not st.session_state.config_twitter):
        bearer_token = st.text_input(
            "Bearer Token (obrigatório)",
            type="password",
            value=config_salva.get('bearer_token', '') if config_salva else ""
        )

        if st.button("Salvar configurações"):
            if bearer_token:
                from coleta_twitter_api import ConfigTwitter

                # Criar configuração
                config_twitter = ConfigTwitter(
                    bearer_token=bearer_token,
                    api_key="",
                    api_secret="",
                    access_token="",
                    access_token_secret=""
                )

                # Salvar na sessão
                st.session_state.config_twitter = config_twitter

                # Salvar em arquivo
                os.makedirs('config', exist_ok=True)
                config_dict = {
                    'bearer_token': bearer_token,
                    'api_key': "",
                    'api_secret': "",
                    'access_token': "",
                    'access_token_secret': ""
                }

                try:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config_dict, f, ensure_ascii=False, indent=2)
                    st.success("✅ Configurações salvas com sucesso!")
                except Exception:
                    st.warning("⚠️ Configurações aplicadas, mas não foi possível salvá-las permanentemente.")
            else:
                st.error("❌ O Bearer Token é obrigatório.")
