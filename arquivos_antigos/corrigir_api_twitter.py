#!/usr/bin/env python3
"""
Script para corrigir o problema de autenticação da API do Twitter
e implementar o salvamento das configurações
"""

import os
import re
import json
import sys

# Caminho para o diretório de configuração
CONFIG_DIR = 'config'
CONFIG_FILE = 'twitter_api.json'

def criar_diretorio_config():
    """Cria o diretório de configuração se não existir"""
    if not os.path.exists(CONFIG_DIR):
        print(f"Criando diretório de configuração: {CONFIG_DIR}")
        os.makedirs(CONFIG_DIR, exist_ok=True)

def modificar_app_py(app_py_path):
    """
    Modifica o arquivo app.py para adicionar o campo de Bearer Token
    e implementar o salvamento das configurações

    Args:
        app_py_path (str): Caminho para o arquivo app.py
    """
    print(f"Modificando arquivo para corrigir autenticação da API: {app_py_path}")

    # Verifica se o arquivo existe
    if not os.path.exists(app_py_path):
        print(f"Erro: Arquivo {app_py_path} não encontrado.")
        return

    # Lê o conteúdo do arquivo
    with open(app_py_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 1. Adiciona a importação do módulo de gerenciamento de configurações
    import_pattern = r'from nlp_relatorios import ProcessadorNLTK, GeradorRelatorios, plotly_para_streamlit'
    import_replacement = """from nlp_relatorios import ProcessadorNLTK, GeradorRelatorios, plotly_para_streamlit
    # Importação do módulo de configuração
    from config_manager import salvar_config_twitter, carregar_config_twitter"""

    content = content.replace(import_pattern, import_replacement)

    # 2. Modificar a inicialização de sessão para carregar configurações salvas
    init_session_pattern = r'def inicializar_sessao\(self\):\s+"""Inicializa variáveis de sessão"""\s+'
    init_session_pattern += r'if \'dados_processados\' not in st\.session_state:\s+st\.session_state\.dados_processados = pd\.DataFrame\(\)\s+'
    init_session_pattern += r'if \'ultima_atualizacao\' not in st\.session_state:\s+st\.session_state\.ultima_atualizacao = None\s+'
    init_session_pattern += r'if \'config_twitter\' not in st\.session_state:\s+st\.session_state\.config_twitter = None\s+'

    init_session_replacement = """def inicializar_sessao(self):
        """Inicializa variáveis de sessão"""
        if 'dados_processados' not in st.session_state:
            st.session_state.dados_processados = pd.DataFrame()
        
        if 'ultima_atualizacao' not in st.session_state:
            st.session_state.ultima_atualizacao = None
        
        if 'config_twitter' not in st.session_state:
            # Tenta carregar as configurações salvas
            config_salva = carregar_config_twitter()
            if config_salva:
                st.session_state.config_twitter = ConfigTwitter(
                    bearer_token=config_salva.get('bearer_token', ''),
                    api_key=config_salva.get('api_key', ''),
                    api_secret=config_salva.get('api_secret', ''),
                    access_token=config_salva.get('access_token', ''),
                    access_token_secret=config_salva.get('access_token_secret', '')
                )
            else:
                st.session_state.config_twitter = None
        
        """

    # Tentar substituir o padrão de inicialização da sessão
    try:
        content_new = re.sub(init_session_pattern, init_session_replacement, content, flags=re.DOTALL)
        if content_new == content:
            print("⚠️ Não foi possível encontrar o padrão exato para inicialização da sessão")
        else:
            content = content_new
    except Exception as e:
        print(f"Erro ao modificar inicialização da sessão: {e}")

    # 3. Modificar a seção de configuração da API do Twitter para incluir Bearer Token
    twitter_config_pattern = r'# Seção de Configuração API Twitter\s+st\.subheader\("🐦 Configuração Twitter API"\)\s+with st\.expander\("Configurar API do Twitter", expanded=not st\.session_state\.config_twitter\):\s+api_key = st\.text_input\("API Key", type="password"\)\s+api_secret = st\.text_input\("API Secret", type="password"\)\s+access_token = st\.text_input\("Access Token", type="password"\)\s+access_secret = st\.text_input\("Access Token Secret", type="password"\)'

    twitter_config_replacement = """# Seção de Configuração API Twitter
            st.subheader("🐦 Configuração Twitter API")
            with st.expander("Configurar API do Twitter", expanded=not st.session_state.config_twitter):
                # Campo de Bearer Token (essencial para API v2)
                bearer_token = st.text_input(
                    "Bearer Token (Obrigatório para API v2)", 
                    type="password",
                    value=st.session_state.config_twitter.bearer_token if st.session_state.config_twitter else ""
                )
                
                st.markdown("---")
                st.markdown("**Opcionais (não necessários se Bearer Token for fornecido):**")
                
                # Campos opcionais para API v1.1 (legacy)
                api_key = st.text_input(
                    "API Key", 
                    type="password",
                    value=st.session_state.config_twitter.api_key if st.session_state.config_twitter else ""
                )
                api_secret = st.text_input(
                    "API Secret", 
                    type="password",
                    value=st.session_state.config_twitter.api_secret if st.session_state.config_twitter else ""
                )
                access_token = st.text_input(
                    "Access Token", 
                    type="password",
                    value=st.session_state.config_twitter.access_token if st.session_state.config_twitter else ""
                )
                access_secret = st.text_input(
                    "Access Token Secret", 
                    type="password",
                    value=st.session_state.config_twitter.access_token_secret if st.session_state.config_twitter else ""
                )"""

    # Tentar substituir o padrão de configuração do Twitter
    try:
        content_new = re.sub(twitter_config_pattern, twitter_config_replacement, content, flags=re.DOTALL)
        if content_new == content:
            print("⚠️ Não foi possível encontrar o padrão exato para configuração da API do Twitter")
        else:
            content = content_new
    except Exception as e:
        print(f"Erro ao modificar configuração da API do Twitter: {e}")

    # 4. Modificar o botão de salvar configurações para incluir o Bearer Token e salvar em arquivo
    save_button_pattern = r'if st\.button\("Salvar configurações"\):\s+if api_key and api_secret and access_token and access_secret:\s+st\.session_state\.config_twitter = ConfigTwitter\(\s+bearer_token="",  # Campo obrigatório\s+api_key=api_key,\s+api_secret=api_secret,\s+access_token=access_token,\s+access_token_secret=access_secret\s+\)\s+st\.success\("✅ Configurações salvas com sucesso!"\)\s+else:\s+st\.error\("⚠️ Preencha todas as configurações\."\)'

    save_button_replacement = """if st.button("Salvar configurações"):
                    if bearer_token:
                        # Criar a configuração
                        st.session_state.config_twitter = ConfigTwitter(
                            bearer_token=bearer_token,
                            api_key=api_key,
                            api_secret=api_secret,
                            access_token=access_token,
                            access_token_secret=access_secret
                        )
                        
                        # Salvar em arquivo para uso futuro
                        config_dict = {
                            'bearer_token': bearer_token,
                            'api_key': api_key,
                            'api_secret': api_secret,
                            'access_token': access_token,
                            'access_token_secret': access_secret
                        }
                        
                        # Tenta salvar a configuração
                        if salvar_config_twitter(config_dict):
                            st.success("✅ Configurações salvas com sucesso! Não será necessário digitá-las novamente.")
                        else:
                            st.warning("✅ Configurações aplicadas, mas não foi possível salvá-las permanentemente.")
                    else:
                        st.error("⚠️ O Bearer Token é obrigatório para a API v2 do Twitter.")"""

    # Tentar substituir o padrão do botão de salvar
    try:
        content_new = re.sub(save_button_pattern, save_button_replacement, content, flags=re.DOTALL)
        if content_new == content:
            print("⚠️ Não foi possível encontrar o padrão exato para o botão de salvar configurações")
        else:
            content = content_new
    except Exception as e:
        print(f"Erro ao modificar o botão de salvar configurações: {e}")

    # Salva o arquivo modificado
    with open(app_py_path, 'w', encoding='utf-8') as file:
        file.write(content)

    print("✅ Arquivo app.py modificado com sucesso")

def main():
    """Função principal"""
    print("🔄 Script para corrigir autenticação da API do Twitter iniciado")

    # Determina o diretório raiz do projeto
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Cria o diretório de configuração se não existir
    criar_diretorio_config()

    # Caminhos para arquivos
    app_py_path = os.path.join(script_dir, 'app.py')

    # Modifica o arquivo app.py
    modificar_app_py(app_py_path)

    print("\n✅ Operação concluída! Reinicie a aplicação para ver as mudanças.")

if __name__ == "__main__":
    main()
