#!/usr/bin/env python3
"""
Script para aplicar o patch da API do Twitter no app.py
"""

import os
import re

def aplicar_patch_app_py(app_py_path):
    """
    Aplica o patch no arquivo app.py

    Args:
        app_py_path (str): Caminho para o arquivo app.py
    """
    print(f"Aplicando patch no arquivo: {app_py_path}")

    # Verifica se o arquivo existe
    if not os.path.exists(app_py_path):
        print(f"Erro: Arquivo {app_py_path} não encontrado.")
        return False

    # Lê o conteúdo do arquivo
    with open(app_py_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 1. Adicionar a importação do config_manager
    import_pattern = r'from correcao_filtros import garantir_colunas_necessarias, aplicar_filtros_seguros'
    import_replacement = 'from correcao_filtros import garantir_colunas_necessarias, aplicar_filtros_seguros\n\n# Importa o gerenciador de configurações\nfrom config_manager import salvar_config_twitter, carregar_config_twitter'

    content = content.replace(import_pattern, import_replacement)

    # 2. Modificar o início da função construir_interface para aplicar o patch
    interface_pattern = r'def construir_interface\(self\):\s+"""Constrói a interface principal do Streamlit"""\s+# Título principal'
    interface_replacement = 'def construir_interface(self):\n        """Constrói a interface principal do Streamlit"""\n        \n        # Aplicar patch da API do Twitter\n        import patch_api_twitter\n        \n        # Título principal'

    content = content.replace(interface_pattern, interface_replacement)

    # 3. Substituir a seção de configuração da API do Twitter para usar apenas o Bearer Token
    config_twitter_pattern = r'# Seção de Configuração API Twitter\s+st\.subheader\("🐦 Configuração Twitter API"\)\s+with st\.expander\("Configurar API do Twitter", expanded=not st\.session_state\.config_twitter\):\s+api_key = st\.text_input\("API Key", type="password"\)\s+api_secret = st\.text_input\("API Secret", type="password"\)\s+access_token = st\.text_input\("Access Token", type="password"\)\s+access_secret = st\.text_input\("Access Token Secret", type="password"\)\s+if st\.button\("Salvar configurações"\):\s+if api_key and api_secret and access_token and access_secret:\s+st\.session_state\.config_twitter = ConfigTwitter\(\s+bearer_token="",\s+api_key=api_key,\s+api_secret=api_secret,\s+access_token=access_token,\s+access_token_secret=access_secret\s+\)\s+st\.success\("✅ Configurações salvas com sucesso!"\)\s+else:\s+st\.error\("⚠️ Preencha todas as configurações\."\)'

    config_twitter_replacement = '''# Seção de Configuração API Twitter
            st.subheader("🐦 Configuração Twitter API")
            with st.expander("Configurar API do Twitter", expanded=not st.session_state.config_twitter):
                bearer_token = st.text_input("Bearer Token (obrigatório)", type="password")

                if st.button("Salvar configurações"):
                    if bearer_token:
                        st.session_state.config_twitter = ConfigTwitter(
                            bearer_token=bearer_token,
                            api_key="",
                            api_secret="",
                            access_token="",
                            access_token_secret=""
                        )
                        # Salvar configurações para uso futuro
                        salvar_config_twitter(st.session_state.config_twitter)
                        st.success("✅ Configurações salvas com sucesso!")
                    else:
                        st.error("⚠️ O Bearer Token é obrigatório.")'''

    # Usar regex para substituir, permitindo espaços em branco flexíveis
    content = re.sub(config_twitter_pattern, config_twitter_replacement, content)

    # Salva o arquivo modificado
    with open(app_py_path, 'w', encoding='utf-8') as file:
        file.write(content)

    print("✅ Patch aplicado com sucesso no app.py")
    return True

def main():
    """Função principal"""
    print("🔄 Aplicando patch da API do Twitter no app.py")

    # Determina o diretório raiz do projeto
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Caminho para o arquivo app.py
    app_py_path = os.path.join(script_dir, 'app.py')

    # Aplica o patch
    if aplicar_patch_app_py(app_py_path):
        print("\n✅ Operação concluída com sucesso!")
        print("Agora a aplicação usará o Bearer Token para a API do Twitter e salvará suas configurações.")
        print("Para executar a aplicação, use o comando: streamlit run app.py")
    else:
        print("\n❌ Não foi possível aplicar o patch.")
        print("Consulte o arquivo 'corrigir_api_twitter_instrucoes.md' para instru��ões manuais.")

if __name__ == "__main__":
    main()
