#!/usr/bin/env python3
"""
Script para corrigir o erro de sintaxe no wordcloud_gen.py causado pela substituição incorreta de emojis
"""

import os

def corrigir_emoji_wordcloud_gen(wordcloud_gen_path):
    """
    Corrige o erro de sintaxe no wordcloud_gen.py substituindo o código HTML por texto simples

    Args:
        wordcloud_gen_path (str): Caminho para o arquivo wordcloud_gen.py
    """
    print(f"Corrigindo erro de sintaxe em: {wordcloud_gen_path}")

    # Verifica se o arquivo existe
    if not os.path.exists(wordcloud_gen_path):
        print(f"Erro: Arquivo {wordcloud_gen_path} não encontrado.")
        return

    # Lê o conteúdo atual do arquivo
    try:
        with open(wordcloud_gen_path, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
    except Exception as e:
        print(f"Erro ao ler o arquivo: {str(e)}")
        return

    # Encontra e corrige as linhas com problemas na legenda
    linhas_corrigidas = False
    for i, linha in enumerate(linhas):
        if "legenda_texto = [" in linha:
            # Encontramos o início da lista de legenda, agora vamos substituir as próximas linhas
            if i+1 < len(linhas) and '<i class=' in linhas[i+1]:
                linhas[i+1] = '            "■ Vermelho: Emergência crítica",\n'
                linhas_corrigidas = True
            if i+2 < len(linhas) and '<i class=' in linhas[i+2]:
                linhas[i+2] = '            "■ Laranja: Alta urgência",\n'
                linhas_corrigidas = True
            if i+3 < len(linhas) and '<i class=' in linhas[i+3]:
                linhas[i+3] = '            "■ Azul: Moderada",\n'
                linhas_corrigidas = True
            if i+4 < len(linhas) and '<i class=' in linhas[i+4]:
                linhas[i+4] = '            "■ Cinza: Baixa frequência"\n'
                linhas_corrigidas = True
            break

    # Salva o arquivo modificado
    if linhas_corrigidas:
        try:
            with open(wordcloud_gen_path, 'w', encoding='utf-8') as f:
                f.writelines(linhas)
            print("✓ Arquivo wordcloud_gen.py corrigido com sucesso!")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {str(e)}")
    else:
        print("Nenhuma linha para corrigir foi encontrada.")

if __name__ == "__main__":
    # Caminho relativo para o arquivo wordcloud_gen.py no mesmo diretório
    script_dir = os.path.dirname(os.path.abspath(__file__))
    wordcloud_gen_path = os.path.join(script_dir, "wordcloud_gen.py")

    corrigir_emoji_wordcloud_gen(wordcloud_gen_path)
