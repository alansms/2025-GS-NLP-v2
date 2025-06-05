import http.client
import json
import os

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

# 🗝️ Chave da API e conexão
conn = http.client.HTTPSConnection("google.serper.dev")
headers = {
    'X-API-KEY': '54842e1a8120d7a6760405cd4dd92a6b2abc6924',
    'Content-Type': 'application/json'
}

# 📦 Armazenar resultados únicos por link
resultados_unicos = set()

# Lista para armazenar resultados para o JSON
resultados_json = []

# 🔁 Busca por termo específico dentro de cada filtro
for filtro, termos in consultas.items():
    print(f"\n📌 Categoria: {filtro}")
    for termo in termos:
        payload = json.dumps({
            "q": termo,
            "gl": "br",
            "hl": "pt-br",
            "num": 10,
            "tbs": "qdr:d"
        })

        conn.request("POST", "/news", payload, headers)
        res = conn.getresponse()
        data = res.read()

        try:
            resultado = json.loads(data.decode("utf-8"))
            noticias = resultado.get("news", [])
            if noticias:
                for noticia in noticias:
                    titulo = noticia.get('title', '')
                    link = noticia.get('link', '')
                    if link not in resultados_unicos:
                        resultados_unicos.add(link)
                        print(f"📰 {titulo}")
                        print(f"🔗 {link}\n")
                        resultados_json.append({
                            "categoria": filtro,
                            "termo": termo,
                            "titulo": titulo,
                            "link": link
                        })
            else:
                print(f"⚠️ Nenhuma notícia encontrada para termo: {termo}")
        except Exception as e:
            print(f"❌ Erro ao processar resposta para '{termo}': {e}")

# Salva os resultados em um arquivo JSON
os.makedirs("data", exist_ok=True)

# Caminho completo para salvar o arquivo na pasta 'data'
caminho_arquivo = os.path.join("data", "resultados.json")

with open(caminho_arquivo, "w", encoding="utf-8") as f:
    json.dump(resultados_json, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Resultados salvos em: {caminho_arquivo}")
