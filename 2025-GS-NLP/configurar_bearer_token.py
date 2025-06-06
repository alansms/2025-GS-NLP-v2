#!/usr/bin/env python3
"""
Patch direto para adicionar o campo Bearer Token na barra lateral
Este script é executado independentemente do app.py
"""

import streamlit as st
import os
import json
from coleta_twitter_api import ConfigTwitter

# Configuração da página
st.set_page_config(page_title="Configuração Twitter API", page_icon="🐦", layout="wide")

st.title("🐦 Configuração da API do Twitter")
st.markdown("""
Este utilitário configura o Bearer Token para a API do Twitter.
Após configurar, reinicie a aplicação principal.
""")

# Verifica se existe configuração salva
config_salva = None
config_path = os.path.join('config', 'twitter_api.json')
if os.path.exists(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_salva = json.load(f)
        st.success("✅ Configuração existente carregada!")
    except Exception as e:
        st.error(f"Erro ao carregar configuração: {str(e)}")

# Interface simplificada apenas com Bearer Token
st.subheader("Bearer Token")
st.markdown("O Bearer Token é obrigatório para usar a API v2 do Twitter.")

bearer_token = st.text_input(
    "Bearer Token (obrigatório)",
    type="password",
    value=config_salva.get('bearer_token', '') if config_salva else ""
)

if st.button("Salvar configuração"):
    if bearer_token:
        try:
            # Criar diretório se não existir
            os.makedirs('config', exist_ok=True)

            # Criar configuração
            config_dict = {
                'bearer_token': bearer_token,
                'api_key': "",
                'api_secret': "",
                'access_token': "",
                'access_token_secret': ""
            }

            # Salvar em arquivo
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)

            st.success("✅ Bearer Token salvo com sucesso!")
            st.info("Agora você pode fechar esta janela e reiniciar a aplicação principal.")

        except Exception as e:
            st.error(f"Erro ao salvar configuração: {str(e)}")
    else:
        st.error("❌ O Bearer Token é obrigatório.")

# Exibir instruções
st.markdown("---")
st.subheader("Como obter um Bearer Token")
st.markdown("""
1. Acesse [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Crie um projeto e um aplicativo
3. No painel do aplicativo, vá para "Keys and tokens"
4. Gere ou copie o Bearer Token
5. Cole o token no campo acima
""")

# Status da configuração
st.markdown("---")
st.subheader("Status da configuração")

if config_salva and config_salva.get('bearer_token'):
    st.success("✅ Bearer Token configurado")
    # Mostra apenas os primeiros 5 caracteres por segurança
    token_preview = config_salva.get('bearer_token')[:5] + "..." if config_salva.get('bearer_token') else ""
    st.info(f"Bearer Token: {token_preview}...")
else:
    st.warning("⚠️ Bearer Token não configurado")
