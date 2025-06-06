#!/usr/bin/env python3
"""
Script simplificado para corrigir a autenticação da API do Twitter
"""

import os
import json

# Diretório e arquivo de configuração
CONFIG_DIR = 'config'
CONFIG_FILE = 'twitter_api.json'

def criar_config_manager():
    """Cria o módulo de gerenciamento de configurações"""
    config_manager_content = """\"\"\"
Módulo para salvar e carregar configurações da API do Twitter
\"\"\"

import os
import json
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

def salvar_config_twitter(config):
    \"\"\"
    Salva configurações da API do Twitter em um arquivo local
    
    Args:
        config (dict): Dicionário com as configurações
        
    Returns:
        bool: True se sucesso, False se falha
    \"\"\"
    try:
        # Verifica se o diretório existe
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, 'twitter_api.json')
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {str(e)}")
        return False

def carregar_config_twitter():
    \"\"\"
    Carrega configurações da API do Twitter do arquivo local
    
    Returns:
        dict: Configurações ou None se não encontrado
    \"\"\"
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'twitter_api.json')
        
        if not os.path.exists(config_path):
            return None
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        return config
    except Exception as e:
        print(f"Erro ao carregar configurações: {str(e)}")
        return None
"""

    with open('config_manager.py', 'w', encoding='utf-8') as f:
        f.write(config_manager_content)

    print("✅ Módulo config_manager.py criado com sucesso")

def criar_diretorio_config():
    """Cria o diretório de configuração se não existir"""
    if not os.path.exists(CONFIG_DIR):
        print(f"Criando diretório de configuração: {CONFIG_DIR}")
        os.makedirs(CONFIG_DIR, exist_ok=True)

def criar_patch_api_twitter():
    """Cria um patch para o arquivo app.py"""
    patch_content = """\"\"\"
Patch manual para corrigir o problema da API do Twitter
\"\"\"

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
        api_key=config_salva.get('api_key', ''),
        api_secret=config_salva.get('api_secret', ''),
        access_token=config_salva.get('access_token', ''),
        access_token_secret=config_salva.get('access_token_secret', '')
    )
    
    # Disponibilizar para o aplicativo
    st.session_state.config_twitter = config_twitter

# Interface para configurar API do Twitter
st.sidebar.subheader("🐦 Configurar API do Twitter")
with st.sidebar.expander("Configuração da API", expanded=not config_salva):
    bearer_token = st.text_input(
        "Bearer Token (Obrigatório para API v2)", 
        type="password",
        value=config_salva.get('bearer_token', '') if config_salva else ""
    )
    
    st.markdown("---")
    st.markdown("**Opcionais (não necessários se Bearer Token for fornecido):**")
    
    api_key = st.text_input("API Key", type="password", value=config_salva.get('api_key', '') if config_salva else "")
    api_secret = st.text_input("API Secret", type="password", value=config_salva.get('api_secret', '') if config_salva else "")
    access_token = st.text_input("Access Token", type="password", value=config_salva.get('access_token', '') if config_salva else "")
    access_secret = st.text_input("Access Token Secret", type="password", value=config_salva.get('access_token_secret', '') if config_salva else "")
    
    if st.button("Salvar configurações"):
        if bearer_token:
            # Criar configuração
            config_twitter = ConfigTwitter(
                bearer_token=bearer_token,
                api_key=api_key,
                api_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret
            )
            
            # Salvar na sessão
            st.session_state.config_twitter = config_twitter
            
            # Salvar em arquivo
            config_dict = {
                'bearer_token': bearer_token,
                'api_key': api_key,
                'api_secret': api_secret,
                'access_token': access_token,
                'access_token_secret': access_secret
            }
            
            if salvar_config_twitter(config_dict):
                st.success("✅ Configurações salvas com sucesso! Não será necessário digitá-las novamente.")
            else:
                st.warning("⚠️ Configurações aplicadas, mas não foi possível salvá-las permanentemente.")
        else:
            st.error("❌ O Bearer Token é obrigatório para a API v2 do Twitter.")
"""

    with open('patch_api_twitter.py', 'w', encoding='utf-8') as f:
        f.write(patch_content)

    print("✅ Patch para a API do Twitter criado com sucesso")

def criar_instrucoes():
    """Cria um arquivo de instruções"""
    instrucoes = """# Instruções para Corrigir a API do Twitter

Para corrigir o problema da API do Twitter e permitir que as configurações sejam salvas:

1. Certifique-se de que os arquivos `config_manager.py` e `patch_api_twitter.py` foram criados
2. Adicione a seguinte linha ao início do arquivo `app.py`, logo após as importações:
   ```python
   from config_manager import salvar_config_twitter, carregar_config_twitter
   ```

3. Para uma solução rápida, você pode adicionar a seguinte linha no seu arquivo `app.py` dentro da função `construir_interface`, logo após a definição da barra lateral:
   ```python
   # Adicionar patch para API do Twitter
   import patch_api_twitter
   ```

4. Reinicie a aplicação para ver as mudanças

## Como obter o Bearer Token do Twitter

1. Acesse o portal de desenvolvedores do Twitter: https://developer.twitter.com/
2. Faça login e acesse seu projeto (ou crie um novo)
3. No menu do projeto, acesse "Keys and tokens"
4. Você encontrará o Bearer Token na seção "Authentication Tokens"
5. Copie o Bearer Token e cole no campo correspondente da interface

Observação: O Bearer Token é essencial para usar a API v2 do Twitter, que é a versão atual da API.
"""

    with open('corrigir_api_twitter_instrucoes.md', 'w', encoding='utf-8') as f:
        f.write(instrucoes)

    print("✅ Instruções criadas com sucesso")

def main():
    """Função principal"""
    print("🔄 Script simplificado para corrigir autenticação da API do Twitter iniciado")

    # Criar o diretório de configuração
    criar_diretorio_config()

    # Criar o módulo de gerenciamento de configurações
    criar_config_manager()

    # Criar o patch para a API do Twitter
    criar_patch_api_twitter()

    # Criar instruções
    criar_instrucoes()

    print("\n✅ Operação concluída!")
    print("Siga as instruções no arquivo 'corrigir_api_twitter_instrucoes.md' para aplicar as correções.")

if __name__ == "__main__":
    main()
