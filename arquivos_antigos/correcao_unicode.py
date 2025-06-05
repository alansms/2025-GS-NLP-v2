#!/usr/bin/env python3
"""
Script para corrigir avisos de glifos Unicode faltantes no mapa.py
Substitui os círculos coloridos Unicode por alternativas compatíveis usando Font Awesome
"""

import os
import re

def substituir_caracteres_unicode_no_mapa(mapa_py_path):
    """
    Substitui caracteres Unicode no arquivo mapa.py para evitar avisos de glifos faltantes

    Args:
        mapa_py_path (str): Caminho para o arquivo mapa.py
    """
    print(f"Tentando corrigir caracteres Unicode em: {mapa_py_path}")

    # Verifica se o arquivo existe
    if not os.path.exists(mapa_py_path):
        print(f"Erro: Arquivo {mapa_py_path} não encontrado.")
        return

    # Lê o conteúdo atual do arquivo
    with open(mapa_py_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Modifica a parte que usa cores para indicar urgência no popup
    padrao_popup = re.compile(r'<span style="color: \{\'red\' if urgencia == \'Crítica\' else \'orange\' if urgencia == \'Alta\' else \'blue\'\};">\s*\{urgencia\}\s*</span>')

    substituicao_popup = """<span style="color: {'red' if urgencia == 'Crítica' else 'orange' if urgencia == 'Alta' else 'blue'};">
                    <i class="fa fa-circle" style="color: {'red' if urgencia == 'Crítica' else 'orange' if urgencia == 'Alta' else 'blue'};"></i> {urgencia}
                </span>"""

    conteudo = padrao_popup.sub(substituicao_popup, conteudo)

    # Salva o arquivo modificado
    with open(mapa_py_path, 'w', encoding='utf-8') as f:
        f.write(conteudo)

    print("Arquivo mapa.py atualizado para evitar avisos de glifos Unicode faltantes.")

if __name__ == "__main__":
    # Caminho relativo para o arquivo mapa.py no mesmo diretório
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mapa_py_path = os.path.join(script_dir, "mapa.py")

    substituir_caracteres_unicode_no_mapa(mapa_py_path)
