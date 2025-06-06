# <i class="fa fa-exclamation-triangle" style="color: red;"></i> Monitor de Emergências - Resumo do Projeto

## Visão Geral

O **Monitor de Emergências** é uma aplicação web completa desenvolvida com Streamlit para monitoramento em tempo real de mensagens emergenciais sobre desastres naturais. O sistema coleta dados online, processa com técnicas avançadas de NLP e exibe visualizações interativas para auxiliar na resposta emergencial.

## Principais Funcionalidades Implementadas

✅ **Coleta de Dados em Tempo Real**
- Integração com Twitter API v2
- Sistema de simulação para demonstração
- Armazenamento local em JSON

✅ **Processamento de Linguagem Natural**
- Classificação automática de 10 tipos de desastre
- Análise de sentimento (positivo, negativo, neutro)
- Extração de entidades críticas (telefones, localizações, pessoas)
- Sistema de priorização baseado em urgência

✅ **Dashboard Interativo**
- Interface moderna e responsiva com Streamlit
- Métricas em tempo real
- Filtros por tipo, urgência e período
- Sistema de atualização automática

✅ **Visualizações Avançadas**
- Nuvem de palavras com termos de emergência
- Mapa interativo com localizações das ocorrências
- Gráficos de distribuição e evolução temporal
- Tabela de dados detalhados

## Estrutura do Projeto

```
emergencia_monitor_streamlit/
├── app.py                          # Aplicação principal Streamlit
├── data/
│   └── mensagens_coletadas.json    # Armazenamento local dos dados
├── nlp/
│   ├── analise_sentimento.py       # Análise de sentimento e urgência
│   ├── extrator_entidades.py       # Extração de entidades nomeadas
│   └── classificador_tipo.py       # Classificação de tipos de desastre
├── visuals/
│   ├── wordcloud_gen.py            # Gerador de nuvem de palavras
│   └── mapa.py                     # Componente de mapa interativo
├── utils/
│   └── coleta_twitter_api.py       # Sistema de coleta via Twitter API
├── requirements.txt                # Dependências do projeto
├── README.md                       # Documentação completa
├── INSTRUCOES_EXECUCAO.md          # Guia rápido de execução
└── RESUMO_PROJETO.md               # Este arquivo
```

## Como Executar

1. **Instale as dependências**:
```bash
pip install -r requirements.txt
python -m spacy download pt_core_news_sm
```

2. **Execute a aplicação**:
```bash
streamlit run app.py
```

3. **Acesse** em `http://localhost:8501`

## Tecnologias Utilizadas

- **Backend**: Python 3.11+
- **Interface**: Streamlit
- **NLP**: spaCy, scikit-learn, TextBlob, VADER
- **Visualização**: Plotly, Matplotlib, WordCloud, Folium
- **APIs**: Tweepy (Twitter API v2)
- **Dados**: pandas, numpy

## Documentação

- **README.md**: Documentação completa do projeto
- **INSTRUCOES_EXECUCAO.md**: Guia rápido de execução
- **Comentários no código**: Documentação detalhada de cada módulo

## Próximos Passos Sugeridos

- Integração com mais fontes de dados (Reddit, APIs governamentais)
- Implementação de modelos transformer para melhor precisão
- Sistema de alertas automáticos por email ou SMS
- Exportação de relatórios em PDF
- Implantação em servidor para acesso contínuo

---

**Desenvolvido com ❤️ para ajudar em situações de emergência**

