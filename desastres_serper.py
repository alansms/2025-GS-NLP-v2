import http.client
import json
import os
import random
from datetime import datetime
import uuid
import re

# 🔍 Mapeamento por categoria com termos separados para buscas individuais
consultas = {
    "Enchente": ["enchente", "alagamento", "inundação", "chuvas fortes", "transbordamento de rio"],
    "Deslizamento": ["deslizamento de terra", "desmoronamento", "encosta cedeu"],
    "Terremoto": ["terremoto", "abalo sísmico", "sismo", "tremor de terra"],
    "Incêndio": ["incêndio", "queimada", "fogo em vegetação", "explosão"],
    "Seca": ["seca", "estiagem", "falta de chuva", "crise hídrica", "racionamento de água"],
    "Outro": ["queda de ponte", "desabamento", "colapso de estrutura", "queda de marquise", "queda de muro"],
    "Acidente": ["acidente grave em rodovia", "acidente com morte", "acidente de trânsito", "atropelamento fatal", "engavetamento", "colisão frontal", "acidente de avião", "queda de helicóptero"]
}

# Localizações comuns para desastres no Brasil
localizacoes_brasil = [
    "São Paulo, SP", "Rio de Janeiro, RJ", "Belo Horizonte, MG",
    "Salvador, BA", "Recife, PE", "Fortaleza, CE", "Manaus, AM",
    "Porto Alegre, RS", "Curitiba, PR", "Brasília, DF",
    "Petrópolis, RJ", "Blumenau, SC", "São Sebastião, SP",
    "Angra dos Reis, RJ", "Campos do Jordão, SP"
]

# Lista de estados brasileiros para detecção de localização
estados_brasil = {
    'AC': 'Acre',
    'AL': 'Alagoas',
    'AP': 'Amapá',
    'AM': 'Amazonas',
    'BA': 'Bahia',
    'CE': 'Ceará',
    'DF': 'Distrito Federal',
    'ES': 'Espírito Santo',
    'GO': 'Goiás',
    'MA': 'Maranhão',
    'MT': 'Mato Grosso',
    'MS': 'Mato Grosso do Sul',
    'MG': 'Minas Gerais',
    'PA': 'Pará',
    'PB': 'Paraíba',
    'PR': 'Paraná',
    'PE': 'Pernambuco',
    'PI': 'Piauí',
    'RJ': 'Rio de Janeiro',
    'RN': 'Rio Grande do Norte',
    'RS': 'Rio Grande do Sul',
    'RO': 'Rondônia',
    'RR': 'Roraima',
    'SC': 'Santa Catarina',
    'SP': 'São Paulo',
    'SE': 'Sergipe',
    'TO': 'Tocantins'
}

# Lista de principais cidades brasileiras para detecção
principais_cidades = [
    'São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza',
    'Belo Horizonte', 'Manaus', 'Curitiba', 'Recife', 'Porto Alegre',
    'Belém', 'Goiânia', 'Guarulhos', 'Campinas', 'São Luís',
    'São Gonçalo', 'Maceió', 'Duque de Caxias', 'Natal', 'Teresina',
    'Campo Grande', 'São Bernardo do Campo', 'João Pessoa', 'Santo André',
    'Osasco', 'Jaboatão dos Guararapes', 'Ribeirão Preto', 'Uberlândia',
    'Sorocaba', 'Contagem', 'Aracaju', 'Feira de Santana', 'Cuiabá',
    'Joinville', 'Juiz de Fora', 'Londrina', 'Aparecida de Goiânia',
    'Niterói', 'Ananindeua', 'Porto Velho', 'Serra', 'Caxias do Sul',
    'Macapá', 'Florianópolis', 'Vila Velha', 'Mauá', 'Santos',
    'São José do Rio Preto', 'Mogi das Cruzes', 'Betim', 'Diadema',
    'Campina Grande', 'Jundiaí', 'Maringá', 'Montes Claros', 'Piracicaba',
    'Carapicuíba', 'Bauru', 'Anápolis', 'Olinda', 'Cariacica', 'Rio Branco',
    'Cascavel', 'Vitória', 'Pelotas', 'Guarujá', 'Ribeirão das Neves',
    'Paulista', 'Uberaba', 'Petrolina', 'São José dos Campos', 'Boa Vista',
    'Canoas', 'Blumenau', 'Petrópolis', 'Angra dos Reis', 'Campos do Jordão'
]

# 🗝️ Chave da API e conexão
conn = http.client.HTTPSConnection("google.serper.dev")
headers = {
    'X-API-KEY': '54842e1a8120d7a6760405cd4dd92a6b2abc6924',
    'Content-Type': 'application/json'
}

def extrair_localizacao(texto):
    """
    Extrai localização do texto da notícia utilizando regras e padrões

    Args:
        texto (str): Texto completo da notícia (título + snippet)

    Returns:
        list: Lista de dicionários com localizações encontradas
    """
    localizacoes = []
    texto_original = texto
    texto = texto.lower()

    # Padrão para detectar "em [Cidade]" ou "em [Cidade], [Estado]"
    padrao_em_cidade = r'em\s+([A-Z][a-zÀ-ú]+(?:\s+[A-Z][a-zÀ-ú]+)*)'
    padrao_em_cidade_estado = r'em\s+([A-Z][a-zÀ-ú]+(?:\s+[A-Z][a-zÀ-ú]+)*),\s*([A-Z]{2})'

    # Padrão para "no/na [Cidade]"
    padrao_no_na_cidade = r'n[oa]\s+([A-Z][a-zÀ-ú]+(?:\s+[A-Z][a-zÀ-ú]+)*)'

    # Verificar menções diretas a "Rio", "Rio de Janeiro", etc.
    mencoes_rio = ["rio", "rio de janeiro", "rj"]
    for mencao in mencoes_rio:
        if mencao in texto:
            loc = {"texto": "Rio de Janeiro, RJ", "tipo": "cidade"}
            if loc not in localizacoes:
                localizacoes.append(loc)
                # Se encontrou "Rio" explicitamente, prioriza esta localização
                if mencao in ["rio", "rio de janeiro"]:
                    return localizacoes

    # Verificar primeiros estados (siglas) no texto
    for sigla, nome in estados_brasil.items():
        if f" {sigla.lower()}" in texto or f", {sigla.lower()}" in texto or f"-{sigla.lower()}" in texto:
            # Buscar cidade próxima à sigla
            indices = [m.start() for m in re.finditer(f" {sigla.lower()}", texto)]
            indices.extend([m.start() for m in re.finditer(f", {sigla.lower()}", texto)])
            indices.extend([m.start() for m in re.finditer(f"-{sigla.lower()}", texto)])

            for indice in indices:
                # Buscar cidade antes da sigla (até 50 caracteres antes)
                trecho_anterior = texto[max(0, indice-50):indice]

                # Verificar principais cidades no trecho
                for cidade in principais_cidades:
                    if cidade.lower() in trecho_anterior:
                        loc = {"texto": f"{cidade}, {sigla}", "tipo": "cidade"}
                        if loc not in localizacoes:
                            localizacoes.append(loc)

    # Verificar principais cidades
    for cidade in principais_cidades:
        if cidade.lower() in texto:
            # Verificar se há algum estado próximo
            indice = texto.find(cidade.lower())
            trecho_posterior = texto[indice:indice+30]

            estado_encontrado = False
            for sigla in estados_brasil.keys():
                if sigla.lower() in trecho_posterior:
                    loc = {"texto": f"{cidade}, {sigla}", "tipo": "cidade"}
                    if loc not in localizacoes:
                        localizacoes.append(loc)
                    estado_encontrado = True
                    break

            if not estado_encontrado:
                loc = {"texto": cidade, "tipo": "cidade"}
                if not any(l["texto"] == cidade for l in localizacoes):
                    localizacoes.append(loc)

    # Buscar menções completas no texto original usando regex
    # Para padrões como "em São Paulo"
    matches = re.finditer(padrao_em_cidade, texto_original)
    for match in matches:
        cidade = match.group(1).strip()
        if len(cidade) > 3:  # Filtrar nomes muito curtos
            loc = {"texto": cidade, "tipo": "cidade"}
            if not any(cidade in l["texto"] for l in localizacoes):
                localizacoes.append(loc)

    # Para padrões como "no Rio", "na Bahia"
    matches = re.finditer(padrao_no_na_cidade, texto_original)
    for match in matches:
        cidade = match.group(1).strip()
        if len(cidade) > 2:  # Aceita "Rio" com 3 letras
            # Caso especial para "Rio"
            if cidade.lower() == "rio":
                loc = {"texto": "Rio de Janeiro, RJ", "tipo": "cidade"}
            else:
                loc = {"texto": cidade, "tipo": "cidade"}

            if not any(loc["texto"] in l["texto"] for l in localizacoes):
                localizacoes.append(loc)

    # Para padrões como "em São Paulo, SP"
    matches = re.finditer(padrao_em_cidade_estado, texto_original)
    for match in matches:
        cidade = match.group(1).strip()
        estado = match.group(2).strip()
        if len(cidade) > 3:  # Filtrar nomes muito curtos
            loc = {"texto": f"{cidade}, {estado}", "tipo": "cidade"}
            if not any(f"{cidade}, {estado}" in l["texto"] for l in localizacoes):
                localizacoes.append(loc)

    return localizacoes

def coletar_dados_serper(max_resultados_por_termo=5, salvar_arquivo=True):
    """
    Coleta dados de notícias sobre desastres naturais usando a API Serper (Google)

    Args:
        max_resultados_por_termo (int): Número máximo de resultados por termo de busca
        salvar_arquivo (bool): Se True, salva os resultados em arquivos JSON

    Returns:
        dict: Dicionário com as mensagens coletadas e data de atualização
    """
    # 📦 Armazenar resultados únicos por link
    resultados_unicos = set()

    # Lista para armazenar resultados para o JSON
    resultados_json = []

    # Níveis de urgência possíveis
    niveis_urgencia = ["Alto", "Médio", "Baixo"]

    # Chave da API
    api_key = '54842e1a8120d7a6760405cd4dd92a6b2abc6924'

    # 🔁 Busca por termo específico dentro de cada filtro
    for filtro, termos in consultas.items():
        print(f"\n📌 Categoria: {filtro}")
        for termo in termos:
            # Criar uma nova conexão para cada requisi��ão
            conn = http.client.HTTPSConnection("google.serper.dev")

            # Configurar headers com a API key
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }

            payload = json.dumps({
                "q": termo,
                "gl": "br",
                "hl": "pt-br",
                "num": max_resultados_por_termo,
                "tbs": "qdr:d"
            })

            try:
                # Enviar requisição
                conn.request("POST", "/news", payload, headers)
                res = conn.getresponse()
                data = res.read()
                conn.close()  # Fechar conexão após uso

                resultado = json.loads(data.decode("utf-8"))
                noticias = resultado.get("news", [])
                if noticias:
                    for noticia in noticias:
                        titulo = noticia.get('title', '')
                        link = noticia.get('link', '')
                        snippet = noticia.get('snippet', '')
                        publishedDate = noticia.get('publishedDate', datetime.now().isoformat())

                        if link not in resultados_unicos:
                            resultados_unicos.add(link)
                            print(f"📰 {titulo}")
                            print(f"🔗 {link}\n")

                            # Determinar nível de urgência baseado em palavras-chave no título/snippet
                            nivel_urgencia = "Médio"  # Padrão
                            palavras_alta_urgencia = ["urgente", "grave", "fatal", "mortos", "vítimas", "destruição"]
                            palavras_baixa_urgencia = ["pequeno", "leve", "controlado", "alerta", "possível"]

                            texto_completo = (titulo + " " + snippet).lower()
                            if any(palavra in texto_completo for palavra in palavras_alta_urgencia):
                                nivel_urgencia = "Alto"
                                score_urgencia = random.uniform(0.7, 1.0)
                                sentimento = random.choice(["negativo", "muito negativo"])
                                score_sentimento = -random.uniform(0.6, 1.0)
                            elif any(palavra in texto_completo for palavra in palavras_baixa_urgencia):
                                nivel_urgencia = "Baixo"
                                score_urgencia = random.uniform(0.1, 0.4)
                                sentimento = random.choice(["neutro", "negativo"])
                                score_sentimento = -random.uniform(0.1, 0.3)
                            else:
                                score_urgencia = random.uniform(0.4, 0.7)
                                sentimento = random.choice(["negativo", "neutro"])
                                score_sentimento = -random.uniform(0.3, 0.6)

                            # Extrair localização do texto da notícia
                            texto_para_localidade = titulo + " " + snippet
                            localizacoes_extraidas = extrair_localizacao(texto_para_localidade)

                            # Se não encontrou localização no texto, usar localização aleatória
                            if not localizacoes_extraidas:
                                local_principal = random.choice(localizacoes_brasil)
                                localizacoes_extraidas = [{"texto": local_principal, "tipo": "cidade", "confianca": "baixa"}]

                                # Adicionar segunda localização ocasionalmente
                                if random.random() > 0.7:
                                    segundo_local = random.choice([loc for loc in localizacoes_brasil if loc != local_principal])
                                    localizacoes_extraidas.append({"texto": segundo_local, "tipo": "cidade", "confianca": "baixa"})
                            else:
                                # Adicionar confiança às localizações extraídas
                                for loc in localizacoes_extraidas:
                                    loc["confianca"] = "alta"

                            # Criar entrada completa com todas as colunas necessárias
                            mensagem = {
                                "id": str(uuid.uuid4()),
                                "texto": titulo + " - " + snippet,
                                "data_criacao": publishedDate,
                                "usuario": "SerperAPI",
                                "tipo_desastre": filtro,
                                "nivel_urgencia": nivel_urgencia,
                                "sentimento": sentimento,
                                "score_sentimento": score_sentimento,
                                "score_urgencia": score_urgencia,
                                "localizacoes": localizacoes_extraidas,
                                "telefones": [],
                                "pessoas": [],
                                "fonte": "noticia",
                                "categoria": filtro,
                                "termo": termo,
                                "titulo": titulo,
                                "link": link,
                                "confianca_classificacao": random.uniform(0.7, 0.98),
                                "score_completude": random.uniform(0.5, 0.9)
                            }

                            resultados_json.append(mensagem)
                else:
                    print(f"⚠️ Nenhuma notícia encontrada para termo: {termo}")
            except Exception as e:
                print(f"❌ Erro ao processar resposta para '{termo}': {e}")
                # Tenta fechar a conexão em caso de erro
                try:
                    conn.close()
                except:
                    pass

    # Formatar para JSON no formato esperado pelo aplicativo
    dados_json = {
        'mensagens': resultados_json,
        'ultima_atualizacao': datetime.now().isoformat()
    }

    # Salvar os resultados em arquivos JSON se solicitado
    if salvar_arquivo:
        # Salva os resultados em um arquivo JSON
        os.makedirs("data", exist_ok=True)

        # Caminho completo para salvar o arquivo na pasta 'data'
        caminho_arquivo = os.path.join("data", "resultados.json")

        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            json.dump(dados_json, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Resultados salvos em: {caminho_arquivo}")

        # Não é mais necessário salvar na raiz, apenas na pasta data
        print(f"✅ Os dados foram salvos com sucesso na pasta 'data'")

    return dados_json

# Exemplo de uso
if __name__ == "__main__":
    coletar_dados_serper()
