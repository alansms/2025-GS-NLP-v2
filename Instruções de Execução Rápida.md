# Instruções de Execução Rápida

Este documento contém instruções simplificadas para executar o Monitor de Emergências.

## Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. **Clone ou baixe o projeto**:
```bash
git clone <url-do-repositorio>
cd emergencia_monitor_streamlit
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Instale o modelo spaCy para português** (opcional, para melhor precisão):
```bash
python -m spacy download pt_core_news_sm
```

## Execução

1. **Execute a aplicação Streamlit**:
```bash
streamlit run app.py
```

2. **Acesse a aplicação**:
A aplicação será aberta automaticamente no navegador em `http://localhost:8501`

## Uso Rápido

1. Na barra lateral, clique em "🔄 Coletar Dados" para obter mensagens simuladas
2. Clique em "📊 Processar NLP" para analisar as mensagens
3. Explore as visualizações e métricas no dashboard
4. Use os filtros na barra lateral para refinar os resultados

## Configuração do Twitter API (Opcional)

Para usar dados reais do Twitter:

1. Obtenha um Bearer Token da Twitter API v2
2. Na barra lateral, expanda "🐦 Configurar Twitter API"
3. Insira o Bearer Token e clique em "💾 Salvar Configuração"
4. Clique em "🔄 Coletar Dados" para buscar tweets reais

## Solução de Problemas

- **Erro de importação de módulos**: Execute `pip install -r requirements.txt`
- **Modelo spaCy não encontrado**: Execute `python -m spacy download pt_core_news_sm`
- **Visualizações não carregam**: Verifique se há dados coletados e processados

## Documentação Completa

Para informações detalhadas, consulte o arquivo [README.md](README.md).

