# <i class="fa fa-exclamation-triangle" style="color: red;"></i> Monitor de Emergências - Sistema de Monitoramento em Tempo Real

Sistema completo desenvolvido em Python com Streamlit para monitoramento e análise de mensagens emergenciais sobre desastres naturais em tempo real. A aplicação coleta dados online, processa com técnicas de NLP e exibe visualizações interativas para resposta emergencial.

## 📋 Índice

- [Características Principais](#-características-principais)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Execução](#-execução)
- [Funcionalidades](#-funcionalidades)
- [Módulos do Sistema](#-módulos-do-sistema)
- [API e Coleta de Dados](#-api-e-coleta-de-dados)
- [Exemplos de Uso](#-exemplos-de-uso)
- [Testes](#-testes)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

## 🎯 Características Principais

### ✅ Funcionalidades Implementadas

- **Coleta de Dados em Tempo Real**: Integração com Twitter API v2 para buscar tweets sobre emergências
- **Processamento de Linguagem Natural (NLP)**:
  - Classificação automática do tipo de desastre (enchente, incêndio, deslizamento, etc.)
  - Análise de sentimento com TextBlob e VADER
  - Extração de entidades críticas (telefones, localizações, pessoas)
  - Sistema de priorização baseado em urgência
- **Dashboard Interativo**: Interface moderna e responsiva com Streamlit
- **Visualizações Avançadas**:
  - Nuvem de palavras com termos de emergência
  - Mapa interativo com localizações das ocorrências
  - Gráficos de distribuição e evolução temporal
  - Métricas em tempo real
- **Sistema de Alertas**: Identificação e destaque de emergências críticas
- **Filtros Inteligentes**: Busca por tipo, urgência e período temporal

### 🔧 Tecnologias Utilizadas

- **Backend**: Python 3.11+
- **Interface**: Streamlit
- **NLP**: spaCy, Hugging Face Transformers, TextBlob, VADER
- **Visualização**: Plotly, Matplotlib, WordCloud, Folium
- **Machine Learning**: scikit-learn
- **APIs**: Tweepy (Twitter API v2)
- **Dados**: pandas, numpy

## 📁 Estrutura do Projeto

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
└── README.md                       # Documentação completa
```

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Conta de desenvolvedor Twitter (opcional, para coleta real)

### Passo a Passo

1. **Clone ou baixe o projeto**:
```bash
# Se usando git
git clone <url-do-repositorio>
cd emergencia_monitor_streamlit

# Ou extraia o arquivo ZIP baixado
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Instale modelos de NLP** (opcional, para melhor precisão):
```bash
# Modelo spaCy para português
python -m spacy download pt_core_news_sm
```

## ⚙️ Configuração

### Twitter API (Opcional)

Para coleta de dados reais do Twitter:

1. Crie uma conta de desenvolvedor em [developer.twitter.com](https://developer.twitter.com)
2. Crie um novo projeto/app
3. Obtenha o **Bearer Token** da API v2
4. Configure na interface da aplicação

> **Nota**: O sistema funciona com dados simulados mesmo sem configuração da API

### Configuração de Ambiente

Crie um arquivo `.env` (opcional) para configurações:
```env
TWITTER_BEARER_TOKEN=seu_bearer_token_aqui
```

## 🎮 Execução

### Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação será aberta automaticamente no navegador em `http://localhost:8501`

### Primeira Execução

1. **Acesse a aplicação** no navegador
2. **Configure a API** (opcional) na barra lateral
3. **Clique em "Coletar Dados"** para obter mensagens
4. **Clique em "Processar NLP"** para análise completa
5. **Explore** as visualizações e métricas

## 🔧 Funcionalidades

### 📊 Dashboard Principal

- **Métricas em Tempo Real**: Total de mensagens, emergências críticas, sentimento
- **Gráficos Interativos**: Distribuição por tipo, urgência e evolução temporal
- **Filtros Avançados**: Por tipo de desastre, urgência e período
- **Atualização Automática**: Monitoramento contínuo configurável

### 🗺️ Mapa Interativo

- **Visualização Geográfica**: Localização das emergências no mapa
- **Mapa de Calor**: Densidade de ocorrências por região
- **Marcadores Inteligentes**: Cores e ícones baseados no tipo e urgência
- **Popups Informativos**: Detalhes completos de cada emergência

### ☁️ Nuvem de Palavras

- **Termos Principais**: Palavras mais frequentes nas mensagens
- **Cores Temáticas**: Destaque para termos de emergência
- **Estatísticas**: Análise de frequência e densidade

### <i class="fa fa-exclamation-triangle" style="color: red;"></i> Sistema de Alertas

- **Emergências Críticas**: Destaque automático de situações urgentes
- **Priorização Inteligente**: Score baseado em palavras-chave e sentimento
- **Notificações Visuais**: Interface clara para resposta rápida

## 🧠 Módulos do Sistema

### 1. Análise de Sentimento (`nlp/analise_sentimento.py`)

```python
from nlp.analise_sentimento import AnalisadorSentimento

analisador = AnalisadorSentimento(metodo='vader')
resultado = analisador.analisar_mensagem("Socorro! Enchente muito forte!")

print(resultado['sentimento'])      # 'negativo'
print(resultado['nivel_urgencia'])  # 'alta'
print(resultado['score_urgencia'])  # 8
```

**Características**:
- Suporte a VADER e TextBlob
- Análise de urgência baseada em palavras-chave
- Score de priorização (0-10)
- Detecção de intensificadores

### 2. Extração de Entidades (`nlp/extrator_entidades.py`)

```python
from nlp.extrator_entidades import ExtratorEntidades

extrator = ExtratorEntidades()
resultado = extrator.extrair_todas_entidades(
    "Socorro! Ligue 11 99999-9999 na Rua das Flores, 123"
)

print(resultado['telefones'])     # [{'numero': '11 99999-9999', 'tipo': 'celular'}]
print(resultado['localizacoes'])  # [{'texto': 'Rua das Flores, 123', 'tipo': 'endereco'}]
```

**Características**:
- Extração de telefones (incluindo emergência)
- Identificação de endereços e coordenadas
- Reconhecimento de pessoas e situações críticas
- Score de completude da informação

### 3. Classificação de Desastres (`nlp/classificador_tipo.py`)

```python
from nlp.classificador_tipo import ClassificadorDesastre

classificador = ClassificadorDesastre()
resultado = classificador.classificar_mensagem("Enchente muito forte na região")

print(resultado['tipo_predito'])  # 'enchente'
print(resultado['confianca'])     # 0.85
```

**Características**:
- 10 tipos de desastre suportados
- Modelo supervisionado com scikit-learn
- Confiança baseada em probabilidade + palavras-chave
- Treinamento com dados sintéticos

### 4. Coleta de Dados (`utils/coleta_twitter_api.py`)

```python
from utils.coleta_twitter_api import coletar_dados_emergencia, ConfigTwitter

config = ConfigTwitter(bearer_token="seu_token")
resultado = coletar_dados_emergencia(
    arquivo_saida='dados.json',
    config_twitter=config,
    max_tweets=100
)
```

**Características**:
- Integração com Twitter API v2
- Tratamento de rate limits
- Dados simulados para demonstração
- Armazenamento em JSON

## 📡 API e Coleta de Dados

### Termos de Busca

O sistema monitora automaticamente os seguintes termos:

**Tipos de Desastre**:
- `enchente`, `inundação`, `alagamento`
- `incêndio`, `fogo`, `queimada`
- `deslizamento`, `desmoronamento`
- `vendaval`, `tempestade`, `tornado`
- `granizo`, `terremoto`

**Termos de Emergência**:
- `socorro`, `emergência`, `urgente`
- `bombeiros`, `samu`, `resgate`
- `evacuação`, `desastre`

### Filtros Aplicados

- **Idioma**: Apenas português (`lang:pt`)
- **Localização**: Preferencialmente Brasil (`place_country:BR`)
- **Conteúdo**: Exclui retweets por padrão
- **Período**: Configurável (1h a 7 dias)

## 💡 Exemplos de Uso

### Cenário 1: Monitoramento de Enchentes

1. **Configure filtros**: Tipo = "Enchente", Período = "Últimas 24 horas"
2. **Visualize no mapa**: Concentração geográfica das ocorrências
3. **Analise sentimento**: Proporção de mensagens negativas/urgentes
4. **Identifique padrões**: Horários de pico e regiões mais afetadas

### Cenário 2: Resposta a Emergências

1. **Monitore alertas críticos**: Seção de emergências com urgência "crítica"
2. **Extraia informações**: Telefones e endereços para contato
3. **Priorize atendimento**: Score de urgência para triagem
4. **Acompanhe evolução**: Gráfico temporal da situação

### Cenário 3: Análise de Tendências

1. **Use nuvem de palavras**: Identifique termos emergentes
2. **Compare períodos**: Evolução temporal dos tipos de desastre
3. **Analise distribuição**: Padrões geográficos e sazonais
4. **Gere relatórios**: Exportação de dados para análise externa

## 🧪 Testes

### Teste Básico dos Módulos

```bash
# Teste análise de sentimento
python -c "
from nlp.analise_sentimento import analisar_sentimento_rapido
print(analisar_sentimento_rapido('Socorro! Enchente muito forte!'))
"

# Teste classificação
python -c "
from nlp.classificador_tipo import classificar_desastre_rapido
print(classificar_desastre_rapido('Incêndio de grandes proporções'))
"

# Teste coleta de dados
python -c "
from utils.coleta_twitter_api import coletar_dados_emergencia
resultado = coletar_dados_emergencia('teste.json', usar_simulacao=True, max_tweets=5)
print(f'Coletadas {resultado[\"total_coletado\"]} mensagens')
"
```

### Teste da Aplicação Completa

1. **Execute a aplicação**: `streamlit run app.py`
2. **Gere dados de teste**: Clique em "Coletar Dados"
3. **Processe com NLP**: Clique em "Processar NLP"
4. **Verifique visualizações**: Mapa, gráficos e métricas
5. **Teste filtros**: Aplique diferentes combinações

### Resultados Esperados

- **Coleta**: 20-50 mensagens simuladas por execução
- **Classificação**: Precisão > 70% para tipos principais
- **Sentimento**: Detecção correta de urgência em 80%+ dos casos
- **Entidades**: Extração de telefones e localizações quando presentes
- **Interface**: Carregamento < 5 segundos, visualizações responsivas

## 🔧 Solução de Problemas

### Problemas Comuns

**1. Erro de importação de módulos**
```bash
# Solução: Instalar dependências
pip install -r requirements.txt
```

**2. Modelo spaCy não encontrado**
```bash
# Solução: Baixar modelo português
python -m spacy download pt_core_news_sm
```

**3. Twitter API não funciona**
- Verifique o Bearer Token
- Use modo simulação para testes
- Confirme limites de rate da API

**4. Visualizações não carregam**
- Verifique se há dados coletados
- Execute "Processar NLP" após coleta
- Recarregue a página se necessário

### Logs e Debug

Para debug detalhado, execute:
```bash
streamlit run app.py --logger.level=debug
```

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o projeto
2. **Crie uma branch** para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra um Pull Request**

### Áreas para Melhoria

- **Novos tipos de desastre**: Expandir classificação
- **Mais fontes de dados**: Reddit, RSS, APIs governamentais
- **ML avançado**: Modelos transformer para melhor precisão
- **Alertas automáticos**: Notificações push e email
- **Exportação**: Relatórios PDF e integração com sistemas externos

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

Para dúvidas, problemas ou sugestões:

- **Issues**: Abra uma issue no repositório
- **Documentação**: Consulte este README
- **Exemplos**: Veja a seção de exemplos de uso

---

**Desenvolvido com ❤️ para ajudar em situações de emergência**

*Sistema de Monitoramento de Emergências - Versão 1.0*

