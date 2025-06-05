"""
Módulo de Coleta de Dados via API Serper (Google News)
Coleta notícias em tempo real sobre emergências e desastres naturais
"""

import http.client
import json
import os
import uuid
from datetime import datetime
import pandas as pd
import logging
from typing import Dict, List, Optional, Any

# Configuração de logging
logger = logging.getLogger("serper_noticias")

class ColetorSerper:
    """Classe para coletar notícias sobre desastres via API Serper"""

    def __init__(self, api_key: str = None):
        """Inicializa o coletor com a chave da API"""
        # Usar a chave fornecida ou uma chave padrão
        self.api_key = api_key or '54842e1a8120d7a6760405cd4dd92a6b2abc6924'

        # Mapeamento por categoria com termos separados para buscas individuais
        self.consultas = {
            "Enchente": ["enchente", "alagamento", "inundação", "chuvas fortes", "transbordamento de rio"],
            "Deslizamento": ["deslizamento de terra", "desmoronamento", "encosta cedeu"],
            "Terremoto": ["terremoto", "abalo sísmico", "sismo", "tremor de terra"],
            "Incêndio": ["incêndio florestal", "queimada", "fogo em vegetação", "explosão"],
            "Seca": ["seca", "estiagem", "falta de chuva", "crise hídrica", "racionamento de água"],
            "Outro": ["queda de ponte", "desabamento", "colapso de estrutura", "queda de marquise"]
        }

    def buscar_noticias(self, max_resultados: int = 50) -> List[Dict[str, Any]]:
        """
        Busca notícias para todos os termos de busca e retorna resultados formatados
        para serem compatíveis com o formato de dados do Twitter
        """
        conn = http.client.HTTPSConnection("google.serper.dev")
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

        # Armazenar resultados únicos por link
        resultados_unicos = set()
        resultados = []

        # Contador para limitar o número total de resultados
        total_resultados = 0

        try:
            # Buscar por termo específico dentro de cada filtro
            for filtro, termos in self.consultas.items():
                if total_resultados >= max_resultados:
                    break

                logger.info(f"Buscando notícias para categoria: {filtro}")
                for termo in termos:
                    if total_resultados >= max_resultados:
                        break

                    payload = json.dumps({
                        "q": termo,
                        "gl": "br",
                        "hl": "pt-br",
                        "num": 5,  # Limitamos por termo para não exceder o limite da API
                        "tbs": "qdr:d"  # Últimas 24 horas
                    })

                    try:
                        conn.request("POST", "/news", payload, headers)
                        res = conn.getresponse()
                        data = res.read()

                        resultado = json.loads(data.decode("utf-8"))
                        noticias = resultado.get("news", [])

                        for noticia in noticias:
                            if total_resultados >= max_resultados:
                                break

                            titulo = noticia.get('title', '')
                            link = noticia.get('link', '')
                            snippet = noticia.get('snippet', '')
                            data_pub = noticia.get('date', '')
                            fonte = noticia.get('source', '')

                            # Verificar se já temos esse link para evitar duplicidades
                            if link not in resultados_unicos:
                                resultados_unicos.add(link)

                                # Formatando os dados para serem compatíveis com o formato do Twitter
                                data_formatada = datetime.now().isoformat()
                                texto_completo = f"{titulo}. {snippet}"

                                # Criar um objeto de resultado no formato similar ao Twitter
                                item = {
                                    'id': str(uuid.uuid4()),  # ID único
                                    'texto': texto_completo,
                                    'titulo': titulo,
                                    'data_criacao': data_formatada,
                                    'usuario': fonte,
                                    'link': link,
                                    'tipo_desastre': filtro,  # Já temos a categoria
                                    'termo_busca': termo,
                                    'fonte': 'serper',  # Marcar origem
                                    'localizacoes': self._extrair_localizacoes(texto_completo)
                                }

                                resultados.append(item)
                                total_resultados += 1
                                logger.info(f"Encontrada notícia: {titulo}")

                    except Exception as e:
                        logger.error(f"Erro ao buscar termo '{termo}': {str(e)}")
                        continue

            logger.info(f"Total de notícias coletadas: {len(resultados)}")
            return resultados

        except Exception as e:
            logger.error(f"Erro na busca de notícias: {str(e)}")
            return []

    def _extrair_localizacoes(self, texto: str) -> List[Dict[str, str]]:
        """
        Extrai possíveis localizações do texto de forma simplificada.
        Uma implementação completa usaria NER, mas por simplicidade
        usamos uma abordagem baseada em regras simples.
        """
        # Lista de capitais e estados para detecção simples
        locais_conhecidos = [
            "São Paulo", "Rio de Janeiro", "Belo Horizonte", "Salvador",
            "Recife", "Fortaleza", "Manaus", "Porto Alegre", "Curitiba",
            "Brasília", "Belém", "Goiânia", "SP", "RJ", "MG", "BA", "PE",
            "CE", "AM", "RS", "PR", "DF"
        ]

        localizacoes = []
        for local in locais_conhecidos:
            if local in texto:
                localizacoes.append({"texto": local, "tipo": "cidade"})

        return localizacoes

    def salvar_resultados(self, resultados: List[Dict[str, Any]], caminho: str = None) -> str:
        """Salva os resultados em um arquivo JSON"""
        if not resultados:
            logger.warning("Nenhum resultado para salvar")
            return ""

        # Definir caminho padrão se não fornecido
        if not caminho:
            os.makedirs("data", exist_ok=True)
            caminho = os.path.join("data", "serper_noticias.json")

        try:
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(resultados, f, ensure_ascii=False, indent=2)
            logger.info(f"Resultados salvos em: {caminho}")
            return caminho
        except Exception as e:
            logger.error(f"Erro ao salvar resultados: {str(e)}")
            return ""


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)

    # Criar coletor e buscar notícias
    coletor = ColetorSerper()
    resultados = coletor.buscar_noticias(max_resultados=30)

    # Salvar resultados
    if resultados:
        coletor.salvar_resultados(resultados)
        print(f"Coletadas {len(resultados)} notícias sobre desastres.")
    else:
        print("Não foram encontradas notícias.")
