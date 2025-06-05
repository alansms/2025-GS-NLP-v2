#!/usr/bin/env python3
"""
Script para corrigir o erro de sintaxe no app.py causado pela substituição incorreta do emoji
"""

import os

def corrigir_emoji_app_py(app_py_path):
    """
    Corrige o erro de sintaxe no app.py substituindo o código HTML pelo emoji original

    Args:
        app_py_path (str): Caminho para o arquivo app.py
    """
    print(f"Corrigindo erro de sintaxe em: {app_py_path}")

    # Verifica se o arquivo existe
    if not os.path.exists(app_py_path):
        print(f"Erro: Arquivo {app_py_path} não encontrado.")
        return

    # Lê o conteúdo atual do arquivo
    try:
        with open(app_py_path, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except Exception as e:
        print(f"Erro ao ler o arquivo: {str(e)}")
        return

    # Encontra e corrige a linha com o problema
    linha_corrigida = False
    for i, linha in enumerate(linhas):
        if 'page_icon=' in linha and '<i class=' in linha:
            # Substitui a linha inteira pela versão correta
            linhas[i] = '    page_icon="🚨",\n'
            linha_corrigida = True
            break

    # Salva o arquivo modificado
    if linha_corrigida:
        try:
            with open(app_py_path, 'w', encoding='utf-8') as f:
                f.writelines(linhas)
            print("✓ Arquivo app.py corrigido com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {str(e)}")
    else:
        print("Nenhuma linha para corrigir foi encontrada.")

if __name__ == "__main__":
    # Caminho relativo para o arquivo app.py no mesmo diretório
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_py_path = os.path.join(script_dir, "app.py")

    corrigir_emoji_app_py(app_py_path)
