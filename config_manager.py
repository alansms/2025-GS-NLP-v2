"""
Módulo para salvar e carregar configurações da API do Twitter
"""

import os
import json
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

def salvar_config_twitter(config):
    """
    Salva configurações da API do Twitter em um arquivo local
    
    Args:
        config (dict): Dicionário com as configurações
        
    Returns:
        bool: True se sucesso, False se falha
    """
    try:
        # Verifica se o diretório existe
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, 'twitter_api.json')
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Erro ao salvar configurações: {str(e)}")
        return False

def carregar_config_twitter():
    """
    Carrega configurações da API do Twitter do arquivo local
    
    Returns:
        dict: Configurações ou None se não encontrado
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'twitter_api.json')
        
        if not os.path.exists(config_path):
            return None
            
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        return config
    except Exception as e:
        print(f"Erro ao carregar configurações: {str(e)}")
        return None
