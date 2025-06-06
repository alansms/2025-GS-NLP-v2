#!/usr/bin/env python3
"""
Script para corrigir diretamente o problema do Bearer Token
Esta é uma solução mais direta que edita diretamente o arquivo app.py
"""

import os
import re

def corrigir_config_twitter():
    """
    Substitui a seção de configuração do Twitter no app.py
    para mostrar apenas o campo Bearer Token
    """
    print("🔄 Corrigindo o campo de Bearer Token na interface...")

    # Caminho para o arquivo app.py
    app_py_path = 'app.py'

    # Verifica se o arquivo existe
    if not os.path.exists(app_py_path):
        print(f"❌ Erro: Arquivo {app_py_path} não encontrado.")
        return False

    # Lê o conteúdo do arquivo
    with open(app_py_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Define o padrão para substituir a seção de configuração do Twitter
    pattern = r'# Seção de Configuração API Twitter\s+st\.subheader\("🐦 Configuração Twitter API"\)\s+with st\.expander\("Configurar API do Twitter", expanded=not st\.session_state\.config_twitter\):\s+api_key = st\.text_input\("API Key", type="password"\)\s+api_secret = st\.text_input\("API Secret", type="password"\)\s+access_token = st\.text_input\("Access Token", type="password"\)\s+access_secret = st\.text_input\("Access Token Secret", type="password"\)\s+if st\.button\("Salvar configurações"\):\s+if api_key and api_secret and access_token and access_secret:\s+st\.session_state\.config_twitter = ConfigTwitter\(\s+bearer_token="",\s+api_key=api_key,\s+api_secret=api_secret,\s+access_token=access_token,\s+access_token_secret=access_secret\s+\)\s+st\.success\("✅ Configurações salvas com sucesso!"\)\s+else:\s+st\.error\("⚠️ Preencha todas as configurações\."\)'

    # Define o texto de substituição
    replacement = '''# Seção de Configuração API Twitter
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
                        # Salvar configurações
                        from config_manager import salvar_config_twitter
                        config_dict = {
                            'bearer_token': bearer_token,
                            'api_key': "",
                            'api_secret': "",
                            'access_token': "",
                            'access_token_secret': ""
                        }
                        salvar_config_twitter(config_dict)
                        st.success("✅ Configurações salvas com sucesso!")
                    else:
                        st.error("❌ O Bearer Token é obrigatório.")'''

    # Aplica a substituição usando regex
    new_content = re.sub(pattern, replacement, content)

    # Verifica se a substituição realmente alterou o conteúdo
    if new_content == content:
        print("⚠️ Aviso: Nenhuma alteração foi aplicada. O padrão não foi encontrado.")

        # Tentar uma abordagem mais simples, procurando e substituindo linhas específicas
        lines = content.split('\n')
        target_found = False
        twitter_section_found = False
        section_start = 0
        section_end = 0

        for i, line in enumerate(lines):
            if "# Seção de Configuração API Twitter" in line:
                twitter_section_found = True
                section_start = i
            elif twitter_section_found and "api_key = st.text_input" in line:
                target_found = True
            elif twitter_section_found and "st.subheader(\"🔍 Filtros\")" in line:
                section_end = i
                break

        if twitter_section_found and target_found and section_start < section_end:
            # Recria o conteúdo mantendo tudo antes e depois da seção do Twitter
            new_content = '\n'.join(lines[:section_start]) + '\n'
            new_content += replacement + '\n'
            new_content += '\n'.join(lines[section_end:])
            print("✅ Aplicada correção alternativa.")
        else:
            print("❌ Não foi possível identificar a seção de configuração do Twitter.")
            return False

    # Salva o arquivo modificado
    with open(app_py_path, 'w', encoding='utf-8') as file:
        file.write(new_content)

    print("✅ Correção aplicada com sucesso!")
    return True

if __name__ == "__main__":
    print("🔧 Iniciando correção da interface de configuração do Twitter API...")

    if corrigir_config_twitter():
        print("\n✅ Operação concluída com sucesso!")
        print("Agora a aplicação mostrará apenas o campo Bearer Token para a API do Twitter.")
        print("Para executar a aplicação, use o comando: streamlit run app.py")
    else:
        print("\n❌ Não foi possível aplicar a correção.")
        print("Por favor, tente editar manualmente o arquivo app.py.")
