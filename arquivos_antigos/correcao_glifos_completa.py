#!/usr/bin/env python3
"""
Script para remover todos os glifos Unicode problemáticos do projeto
Este script procura e substitui todos os glifos Unicode de círculos coloridos
que estão causando avisos no Streamlit por alternativas usando Font Awesome
"""

import os
import re
import glob

def substituir_unicode_em_arquivo(arquivo_path):
    """
    Substitui glifos Unicode problemáticos em um arquivo

    Args:
        arquivo_path (str): Caminho do arquivo a ser processado

    Returns:
        bool: True se alterações foram feitas, False caso contrário
    """
    print(f"Processando: {arquivo_path}")

    # Lê o conteúdo atual do arquivo
    with open(arquivo_path, 'r', encoding='utf-8') as f:
        conteudo_original = f.read()

    conteudo = conteudo_original

    # Lista de substituições - tuplas (padrão, substituição)
    substituicoes = [
        # Círculos coloridos Unicode para ícones Font Awesome
        (r'<i class="fa fa-circle" style="color: red;"></i>', '<i class="fa fa-circle" style="color: red;"></i>'),
        (r'<i class="fa fa-circle" style="color: orange;"></i>', '<i class="fa fa-circle" style="color: orange;"></i>'),
        (r'<i class="fa fa-circle" style="color: blue;"></i>', '<i class="fa fa-circle" style="color: blue;"></i>'),
        (r'<i class="fa fa-circle" style="color: white;"></i>', '<i class="fa fa-circle" style="color: white;"></i>'),
        (r'<i class="fa fa-circle" style="color: black;"></i>', '<i class="fa fa-circle" style="color: black;"></i>'),

        # Código Unicode para círculos coloridos (em HTML)
        (r'<i class="fa fa-circle" style="color: red;"></i>', '<i class="fa fa-circle" style="color: red;"></i>'),
        (r'<i class="fa fa-circle" style="color: orange;"></i>', '<i class="fa fa-circle" style="color: orange;"></i>'),
        (r'<i class="fa fa-circle" style="color: blue;"></i>', '<i class="fa fa-circle" style="color: blue;"></i>'),

        # Código Unicode para círculos coloridos (em strings Python)
        (r'\<i class="fa fa-circle" style="color: red;"></i>', '<i class="fa fa-circle" style="color: red;"></i>'),
        (r'\<i class="fa fa-circle" style="color: orange;"></i>', '<i class="fa fa-circle" style="color: orange;"></i>'),
        (r'\<i class="fa fa-circle" style="color: blue;"></i>', '<i class="fa fa-circle" style="color: blue;"></i>'),

        # Círculos coloridos em strings HTML
        (r'<i class="fa fa-circle" style="color: red;"></i>', '<i class="fa fa-circle" style="color: red;"></i>'),
        (r'<i class="fa fa-circle" style="color: orange;"></i>', '<i class="fa fa-circle" style="color: orange;"></i>'),
        (r'<i class="fa fa-circle" style="color: blue;"></i>', '<i class="fa fa-circle" style="color: blue;"></i>'),

        # Outras formas de círculos em strings (caractere <i class="fa fa-circle"></i>)
        (r'<i class="fa fa-circle"></i>', '<i class="fa fa-circle"></i>'),

        # Padrão de popup no mapa.py que usa cores variáveis (urgência)
        (r'<span style="color: \{\'red\' if urgencia == \'Crítica\' else \'orange\' if urgencia == \'Alta\' else \'blue\'\};">\s*\{urgencia\}\s*</span>',
         """<span style="color: {'red' if urgencia == 'Crítica' else 'orange' if urgencia == 'Alta' else 'blue'};">
                    <i class="fa fa-circle" style="color: {'red' if urgencia == 'Crítica' else 'orange' if urgencia == 'Alta' else 'blue'};"></i> {urgencia}
                </span>"""),

        # Para markdown ou texto com emojis
        (r'<i class="fa fa-exclamation-triangle" style="color: red;"></i>', '<i class="fa fa-exclamation-triangle" style="color: red;"></i>'),
    ]

    # Aplica todas as substituições
    for padrao, substituicao in substituicoes:
        conteudo = re.sub(padrao, substituicao, conteudo)

    # Verifica se houve alterações
    if conteudo != conteudo_original:
        # Salva o arquivo modificado
        with open(arquivo_path, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        print(f"✓ Substituições realizadas em: {arquivo_path}")
        return True
    else:
        print(f"✓ Nenhuma substituição necessária em: {arquivo_path}")
        return False

def corrigir_glifos_em_diretorio(diretorio_base):
    """
    Procura e corrige glifos Unicode em todos os arquivos Python do diretório

    Args:
        diretorio_base (str): Diretório base do projeto
    """
    print(f"Procurando arquivos Python em: {diretorio_base}")

    # Encontra todos os arquivos Python no diretório e subdiretórios
    arquivos_python = glob.glob(os.path.join(diretorio_base, "*.py"))
    arquivos_python += glob.glob(os.path.join(diretorio_base, "*/*.py"))

    # Encontra arquivos HTML que possam conter glifos
    arquivos_html = glob.glob(os.path.join(diretorio_base, "*.html"))
    arquivos_html += glob.glob(os.path.join(diretorio_base, "*/*.html"))

    # Encontra arquivos markdown
    arquivos_md = glob.glob(os.path.join(diretorio_base, "*.md"))
    arquivos_md += glob.glob(os.path.join(diretorio_base, "*/*.md"))

    # Combina todos os tipos de arquivos
    todos_arquivos = arquivos_python + arquivos_html + arquivos_md

    print(f"Encontrados {len(todos_arquivos)} arquivos para processar")

    # Processa cada arquivo
    arquivos_alterados = 0
    for arquivo in todos_arquivos:
        if substituir_unicode_em_arquivo(arquivo):
            arquivos_alterados += 1

    print(f"Processamento concluído. {arquivos_alterados} arquivos foram modificados.")

if __name__ == "__main__":
    # Obtém o diretório atual do script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Corrige glifos no diretório do projeto
    corrigir_glifos_em_diretorio(script_dir)

    print("\nTodas as substituições de glifos Unicode foram concluídas!")
    print("Os avisos sobre glifos faltantes devem ser eliminados na próxima execução da aplicação.")
