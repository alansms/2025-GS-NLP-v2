#!/usr/bin/env python3
"""
Script para corrigir o erro de sintaxe específico na linha 232 do wordcloud_gen.py
"""

import os

def corrigir_legenda_wordcloud_gen(wordcloud_gen_path):
    """
    Corrige o erro de sintaxe específico na legenda do wordcloud_gen.py

    Args:
        wordcloud_gen_path (str): Caminho para o arquivo wordcloud_gen.py
    """
    print(f"Corrigindo erro de sintaxe específico em: {wordcloud_gen_path}")

    # Verifica se o arquivo existe
    if not os.path.exists(wordcloud_gen_path):
        print(f"Erro: Arquivo {wordcloud_gen_path} não encontrado.")
        return

    # Lê o conteúdo atual do arquivo
    try:
        with open(wordcloud_gen_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except Exception as e:
        print(f"Erro ao ler o arquivo: {str(e)}")
        return

    # Substitui a lista de legenda problemática por uma versão corrigida
    legenda_problematica = """        legenda_texto = [
            "Cores das palavras:",
            "■ Laranja: Alta urgência",
            "■ Azul: Moderada",
            "■ Cinza: Baixa frequência"
            "<i class="fa fa-circle" style="color: black;"></i> Cinza: Baixa frequência"
        ]"""

    legenda_corrigida = """        legenda_texto = [
            "Cores das palavras:",
            "■ Vermelho: Emergência crítica",
            "■ Laranja: Alta urgência",
            "■ Azul: Moderada",
            "■ Cinza: Baixa frequência"
        ]"""

    if legenda_problematica in conteudo:
        conteudo_corrigido = conteudo.replace(legenda_problematica, legenda_corrigida)

        # Salva o arquivo modificado
        try:
            with open(wordcloud_gen_path, 'w', encoding='utf-8') as f:
                f.write(conteudo_corrigido)
            print("✓ Arquivo wordcloud_gen.py corrigido com sucesso!")
            return True
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {str(e)}")
            return False
    else:
        print("Legenda problemática específica não encontrada. Tentando abordagem alternativa...")

        # Abordagem alternativa: ler linha a linha e reescrever a legenda inteira
        try:
            with open(wordcloud_gen_path, 'r', encoding='utf-8') as f:
                linhas = f.readlines()
        except Exception as e:
            print(f"Erro ao ler o arquivo: {str(e)}")
            return False

        # Encontra o início da legenda
        inicio_legenda = -1
        for i, linha in enumerate(linhas):
            if "legenda_texto = [" in linha:
                inicio_legenda = i
                break

        if inicio_legenda >= 0:
            # Conta o número de linhas da legenda
            fim_legenda = -1
            for i in range(inicio_legenda, len(linhas)):
                if "]" in linhas[i] and "(" not in linhas[i]:
                    fim_legenda = i
                    break

            if fim_legenda > 0:
                # Reescreve a legenda inteira
                nova_legenda = [
                    '        legenda_texto = [\n',
                    '            "Cores das palavras:",\n',
                    '            "■ Vermelho: Emergência crítica",\n',
                    '            "■ Laranja: Alta urgência",\n',
                    '            "■ Azul: Moderada",\n',
                    '            "■ Cinza: Baixa frequência"\n',
                    '        ]\n'
                ]

                # Substitui as linhas da legenda
                linhas[inicio_legenda:fim_legenda+1] = nova_legenda

                # Salva o arquivo
                with open(wordcloud_gen_path, 'w', encoding='utf-8') as f:
                    f.writelines(linhas)

                print("✓ Arquivo wordcloud_gen.py corrigido com sucesso (abordagem alternativa)!")
                return True
            else:
                print("Não foi possível encontrar o fim da legenda.")
                return False
        else:
            print("Não foi possível encontrar o início da legenda.")
            return False

if __name__ == "__main__":
    # Caminho relativo para o arquivo wordcloud_gen.py no mesmo diretório
    script_dir = os.path.dirname(os.path.abspath(__file__))
    wordcloud_gen_path = os.path.join(script_dir, "wordcloud_gen.py")

    corrigir_legenda_wordcloud_gen(wordcloud_gen_path)
