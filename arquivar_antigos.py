#!/usr/bin/env python3
"""
Script para arquivar os arquivos antigos do projeto
Este script move os arquivos da pasta 'arquivos_antigos' para uma pasta 'arquivados' fora do projeto principal
"""

import os
import shutil
from datetime import datetime

# Diretório de origem
SOURCE_DIR = 'arquivos_antigos'

# Diretório de destino com data para organização
current_date = datetime.now().strftime("%Y%m%d")
DEST_DIR = f'../arquivados_{current_date}'

def main():
    """Função principal para arquivar os arquivos antigos"""
    # Verifica se o diretório de origem existe
    if not os.path.exists(SOURCE_DIR):
        print(f"Erro: Diretório {SOURCE_DIR} não encontrado.")
        return False

    # Cria o diretório de destino se não existir
    if not os.path.exists(DEST_DIR):
        print(f"Criando diretório de arquivamento: {DEST_DIR}")
        os.makedirs(DEST_DIR, exist_ok=True)

    # Lista os arquivos no diretório de origem
    arquivos = os.listdir(SOURCE_DIR)

    if not arquivos:
        print(f"Nenhum arquivo encontrado em {SOURCE_DIR}.")
        return False

    # Cria um arquivo README explicando o arquivamento
    with open(os.path.join(DEST_DIR, 'README.txt'), 'w') as f:
        f.write(f"""
Arquivos antigos do projeto "Monitoramento de Desastres Naturais"
Arquivados em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

Estes arquivos foram arquivados por não serem mais necessários para o funcionamento atual do sistema.
Eles incluem scripts de correção, patches e outros arquivos temporários que foram utilizados durante
o desenvolvimento, mas que agora são obsoletos.

Lista de arquivos arquivados:
{', '.join(arquivos)}
""")

    # Move cada arquivo para o diretório de destino
    arquivos_movidos = []
    for arquivo in arquivos:
        origem = os.path.join(SOURCE_DIR, arquivo)
        destino = os.path.join(DEST_DIR, arquivo)

        # Verifica se é um arquivo (não diretório)
        if os.path.isfile(origem):
            try:
                shutil.copy2(origem, destino)
                arquivos_movidos.append(arquivo)
                print(f"Arquivo copiado: {arquivo}")
            except Exception as e:
                print(f"Erro ao copiar {arquivo}: {str(e)}")

    # Após copiar tudo com sucesso, cria um arquivo vazio na pasta original
    # indicando que os arquivos foram arquivados
    if arquivos_movidos:
        with open(os.path.join(SOURCE_DIR, '.arquivado'), 'w') as f:
            f.write(f"Arquivos movidos para {DEST_DIR} em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        print(f"\nArquivamento concluído!")
        print(f"Total de {len(arquivos_movidos)} arquivos movidos para {DEST_DIR}")
        print(f"Os arquivos originais permanecem em {SOURCE_DIR}")
        print(f"Para excluir os arquivos originais, execute: shutil.rmtree('{SOURCE_DIR}')")

    return True

if __name__ == "__main__":
    main()
