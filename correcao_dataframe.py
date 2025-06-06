#!/usr/bin/env python3
"""
Script para corrigir o erro 'Length of values (0) does not match length of index (50)'
Este erro acontece quando há uma incompatibilidade de tamanho em um DataFrame vazio
"""

import os
import re

def corrigir_erro_dataframe_vazio(mapa_py_path):
    """
    Adiciona verificações adicionais para DataFrames vazios em mapa.py

    Args:
        mapa_py_path (str): Caminho para o arquivo mapa.py
    """
    print(f"Tentando corrigir erro de DataFrame vazio em: {mapa_py_path}")

    # Verifica se o arquivo existe
    if not os.path.exists(mapa_py_path):
        print(f"Erro: Arquivo {mapa_py_path} não encontrado.")
        return

    # Lê o conteúdo atual do arquivo
    with open(mapa_py_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Adiciona verificação de dados vazios na função processar_localizacoes
    padrao_processar = re.compile(r'def processar_localizacoes\(self, dados: pd\.DataFrame,.*?\):.*?\n {8}dados_com_coords = \[\]', re.DOTALL)
    substituicao_processar = """def processar_localizacoes(self, dados: pd.DataFrame,
                              coluna_texto: str = 'texto',
                              coluna_tipo: str = 'tipo_desastre',
                              coluna_urgencia: str = 'nivel_urgencia') -> pd.DataFrame:
        \"\"\"
        Processa DataFrame para extrair localizações
        
        Args:
            dados (pd.DataFrame): DataFrame com dados
            coluna_texto (str): Nome da coluna com texto
            coluna_tipo (str): Nome da coluna com tipo de emergência
            coluna_urgencia (str): Nome da coluna com nível de urgência
            
        Returns:
            pd.DataFrame: DataFrame com localizações processadas
        \"\"\"
        # Verifica se o DataFrame está vazio
        if dados.empty:
            print("Aviso: DataFrame vazio passado para processar_localizacoes")
            return pd.DataFrame()
            
        dados_com_coords = []"""

    conteudo = padrao_processar.sub(substituicao_processar, conteudo)

    # Reforça verificação de dados vazios em gerar_estatisticas_mapa
    padrao_stats = re.compile(r'def gerar_estatisticas_mapa\(self, dados: pd\.DataFrame\) -> Dict:.*?\n {8}if dados\.empty:', re.DOTALL)
    substituicao_stats = """def gerar_estatisticas_mapa(self, dados: pd.DataFrame) -> Dict:
        \"\"\"
        Gera estatísticas para o mapa
        
        Args:
            dados (pd.DataFrame): Dados processados
            
        Returns:
            Dict: Estatísticas do mapa
        \"\"\"
        # Verifica se o DataFrame está vazio
        if dados is None or dados.empty:"""

    conteudo = padrao_stats.sub(substituicao_stats, conteudo)

    # Adiciona verificação robusta na função criar_mapa_emergencias_rapido
    padrao_rapido = re.compile(r'def criar_mapa_emergencias_rapido\(dados: pd\.DataFrame,.*?\):.*?\n {4}gerador = GeradorMapaEmergencia\(\)', re.DOTALL)
    substituicao_rapido = """def criar_mapa_emergencias_rapido(dados: pd.DataFrame, 
                                 incluir_calor: bool = True,
                                 agrupar_marcadores: bool = True) -> folium.Map:
    \"\"\"
    Função de conveniência para criar mapa rapidamente
    
    Args:
        dados (pd.DataFrame): Dados com emergências
        incluir_calor (bool): Se deve incluir mapa de calor
        agrupar_marcadores (bool): Se deve agrupar marcadores
        
    Returns:
        folium.Map: Mapa gerado
    \"\"\"
    # Verifica se o DataFrame está vazio ou None
    if dados is None or dados.empty:
        print("Aviso: DataFrame vazio ou None passado para criar_mapa_emergencias_rapido")
        gerador = GeradorMapaEmergencia()
        return gerador.criar_mapa_base()
        
    gerador = GeradorMapaEmergencia()"""

    conteudo = padrao_rapido.sub(substituicao_rapido, conteudo)

    # Salva o arquivo modificado
    with open(mapa_py_path, 'w', encoding='utf-8') as f:
        f.write(conteudo)

    print("Arquivo mapa.py atualizado para lidar melhor com DataFrames vazios.")

if __name__ == "__main__":
    # Caminho relativo para o arquivo mapa.py no mesmo diretório
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mapa_py_path = os.path.join(script_dir, "mapa.py")

    corrigir_erro_dataframe_vazio(mapa_py_path)
