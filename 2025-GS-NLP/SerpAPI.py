from serpapi import GoogleSearch

consultas = [
    "enchente em São Paulo",
    "chuvas fortes no sul do Brasil",
    "ventos perigosos litoral",
    "trânsito parado por deslizamento",
    "frio intenso no sudeste",
    "alagamentos em Belo Horizonte",
    "deslizamento no Rio de Janeiro",
    "temporal no sul",
    "emergência climática no Brasil",
    "alerta de tempestade em Curitiba",
    "quedas de árvores após vendaval",
    "acidente causado por neblina densa",
    "queda de energia em Santa Catarina",
    "granizo causa danos em carros",
    "temperatura negativa no sul do Brasil",
    "estradas interditadas por desmoronamento",
    "alagamento em estação de metrô",
    "chuva causa interdição de escolas",
    "frente fria avança pelo sudeste",
    "alerta laranja do INMET por temporais",
    # Situações simples e genéricas para testes
    "chuva forte",
    "vento forte",
    "trânsito intenso",
    "queda de energia",
    "neblina nas estradas"
]

params_base = {
    "engine": "google",
    "location": "Brazil",
    "hl": "pt",
    "gl": "br",
    "api_key": "SUA_CHAVE_SERPAPI"  # substitua pela sua chave real
}

for consulta in consultas:
    print(f"\n🔍 Resultados para: {consulta}\n" + "-"*50)
    params = params_base.copy()
    params["q"] = consulta
    params["tbm"] = "nws"  # busca apenas por notícias
    params["tbs"] = "qdr:d"  # restringe aos resultados do último dia

    search = GoogleSearch(params)
    results = search.get_dict()

    noticias = results.get("news_results", [])
    if noticias:
        for noticia in noticias:
            print(f"📰 {noticia.get('title')}\n🔗 {noticia.get('link')}\n")
    else:
        print("⚠️ Nenhuma notícia encontrada para essa consulta.\n")