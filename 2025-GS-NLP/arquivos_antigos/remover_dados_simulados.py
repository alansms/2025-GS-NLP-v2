#!/usr/bin/env python3
"""
Script para remover a exibição de dados simulados no Monitor de Emergências
Este script modifica o arquivo app.py para filtrar apenas dados reais da API
"""

import os
import re
import json
import sys

def modificar_app_py(app_py_path):
    """
    Modifica o arquivo app.py para filtrar dados simulados

    Args:
        app_py_path (str): Caminho para o arquivo app.py
    """
    print(f"Modificando arquivo para remover dados simulados: {app_py_path}")

    # Verifica se o arquivo existe
    if not os.path.exists(app_py_path):
        print(f"Erro: Arquivo {app_py_path} não encontrado.")
        return

    # Lê o conteúdo do arquivo
    with open(app_py_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Modifica o método aplicar_filtros para verificar corretamente o campo fonte em vez de origem
    old_filter_code = """        # Primeiro, filtramos para remover dados simulados
        if not df.empty and 'origem' in df.columns:
            # Mantém apenas dados com origem 'api' ou outras origens reais
            df = df[df['origem'] != 'simulado']"""

    new_filter_code = """        # Primeiro, filtramos para remover dados simulados
        if not df.empty:
            # Verifica se existe a coluna 'fonte' ou 'origem'
            if 'fonte' in df.columns:
                # Mantém apenas dados que não são da fonte 'simulado'
                df = df[df['fonte'] != 'simulado']
            elif 'origem' in df.columns:
                # Verifica também a coluna 'origem' por compatibilidade
                df = df[df['origem'] != 'simulado']"""

    # Substitui o código de filtragem
    modified_content = content.replace(old_filter_code, new_filter_code)

    # Se houve modificação, salva o arquivo
    if modified_content != content:
        with open(app_py_path, 'w', encoding='utf-8') as file:
            file.write(modified_content)
        print("✅ Filtro de dados simulados atualizado com sucesso no app.py")
    else:
        print("⚠️ Não foi possível encontrar o padrão exato para substituição no app.py")
        print("Tentando abordagem alternativa...")

        # Abordagem alternativa - procurar por qualquer método aplicar_filtros
        pattern = r'def aplicar_filtros\(self, df: pd\.DataFrame\) -> pd\.DataFrame:.*?return aplicar_filtros_seguros\(df\)'
        replacement = """def aplicar_filtros(self, df: pd.DataFrame) -> pd.DataFrame:
        \"\"\"Aplica filtros aos dados com base nos critérios selecionados\"\"\"
        # Primeiro, filtramos para remover dados simulados
        if not df.empty:
            # Verifica se existe a coluna 'fonte' ou 'origem'
            if 'fonte' in df.columns:
                # Mantém apenas dados que não são da fonte 'simulado'
                df = df[df['fonte'] != 'simulado']
            elif 'origem' in df.columns:
                # Verifica também a coluna 'origem' por compatibilidade
                df = df[df['origem'] != 'simulado']
            
        # Se o DataFrame ficou vazio após filtrar dados simulados
        if df.empty:
            st.warning("Nenhum dado real disponível da API. Apenas dados simulados foram encontrados e foram removidos conforme solicitado.")
            return pd.DataFrame()
            
        # Utilizamos a função segura para garantir que todas as colunas necessárias existam
        return aplicar_filtros_seguros(df)"""

        modified_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        if modified_content != content:
            with open(app_py_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            print("✅ Filtro de dados simulados atualizado com sucesso no app.py (abordagem alternativa)")
        else:
            print("❌ Não foi possível atualizar o filtro no app.py. Modificação manual necessária.")

def limpar_dados_simulados(json_path):
    """
    Remove os dados simulados diretamente do arquivo JSON

    Args:
        json_path (str): Caminho para o arquivo JSON com as mensagens
    """
    print(f"Processando arquivo de dados: {json_path}")

    if not os.path.exists(json_path):
        print(f"Erro: Arquivo {json_path} não encontrado.")
        return

    try:
        # Lê o arquivo JSON
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if 'mensagens' not in data:
            print("Erro: Formato de dados inválido, 'mensagens' não encontrado.")
            return

        # Conta mensagens antes da remoção
        total_antes = len(data['mensagens'])

        # Filtra para remover mensagens simuladas
        mensagens_reais = [msg for msg in data['mensagens']
                           if msg.get('fonte') != 'simulado' and msg.get('origem') != 'simulado']

        # Atualiza o dicionário
        data['mensagens'] = mensagens_reais

        # Conta mensagens após a remoção
        total_depois = len(data['mensagens'])
        removidos = total_antes - total_depois

        # Salva o arquivo atualizado
        with open(json_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        print(f"✅ Dados limpos com sucesso! Removidas {removidos} mensagens simuladas.")
        print(f"   Total antes: {total_antes}, Total depois: {total_depois}")

    except json.JSONDecodeError:
        print("Erro: O arquivo não contém um JSON válido.")
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")

def main():
    """Função principal"""
    print("🔄 Script para remover dados simulados iniciado")

    # Determina o diretório raiz do projeto
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Caminhos para arquivos
    app_py_path = os.path.join(script_dir, 'app.py')
    json_path = os.path.join(script_dir, 'data', 'mensagens_coletadas.json')

    # Modifica o arquivo app.py
    modificar_app_py(app_py_path)

    # Limpa os dados simulados do arquivo JSON
    limpar_dados_simulados(json_path)

    print("\n✅ Operação concluída! Reinicie a aplicação para ver as mudanças.")

if __name__ == "__main__":
    main()
