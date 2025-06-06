# 🚨 Monitor de Emergências - Sistema de Monitoramento em Tempo Real

Sistema de monitoramento e análise de mensagens emergenciais sobre desastres naturais desenvolvido como projeto para a Global Solution da FIAP.

## 🎯 Sobre o Projeto

Este projeto consiste em um sistema avançado de monitoramento de emergências que:

- Coleta dados em tempo real com Serper API com noticias filtradas sobre desastres naturais
- Processa mensagens usando técnicas avançadas de NLP
- Classifica automaticamente tipos de desastres
- Analisa sentimentos e urgência das mensagens
- Extrai entidades críticas (localizações, contatos)
- Fornece visualizações interativas e sistema de alertas

  ![Front End](https://raw.githubusercontent.com/alansms/2025-GS-NLP-v2/main/2025-GS-NLP/img/app.gif)

## 🔧 Tecnologias Principais

- **Backend**: Python 3.11+
- **Interface**: Streamlit
- **NLP**: spaCy, Hugging Face Transformers, TextBlob, VADER
- **Visualização**: Plotly, Matplotlib, WordCloud, Folium
- **Machine Learning**: scikit-learn
- **APIs**: Tweepy (Twitter API v2)
- **Dados**: pandas, numpy

## 🚀 Como executar

### Localmente

1. Clone o repositório:
```bash
git clone https://github.com/alansms/2025-GS-NLP-v2.git
cd 2025-GS-NLP-v2
```

2. Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure o Serper API:
- Crie uma conta em https://serper.dev/
- Obtenha a chave da API
- Configure na interface da aplicação

4. Execute a aplicação:
```bash
streamlit run app.py
```

## 📊 Funcionalidades

### Dashboard Principal
- Métricas em tempo real de emergências
- Visualização geográfica em mapa interativo
- Nuvem de palavras com termos emergenciais
- Gráficos de distribuição e evolução temporal

### Sistema de Alertas
- Identificação automática de emergências críticas
- Priorização baseada em urgência
- Análise de sentimento das mensagens
- Notificações visuais em tempo real

### Processamento NLP
- Classificação de tipos de desastre
- Extração de entidades (locais, contatos)
- Análise de sentimento com VADER
- Sistema de pontuação de urgência

### Visualização de Dados
- Mapa interativo com ocorrências
- Gráficos de distribuição
- Métricas em tempo real
- Filtros avançados por tipo e região

## 🛠 Estrutura do Projeto

```
2025-GS-NLP/
├── app.py                    # Aplicação principal
├── nlp/                      # Módulos de processamento
│   ├── analise_sentimento.py
│   ├── classificador_tipo.py
│   └── extrator_entidades.py
├── visuals/                  # Componentes visuais
│   ├── mapa.py
│   └── wordcloud_gen.py
├── data/                     # Dados processados
└── config/                   # Configurações
```

## 📝 Requisitos do Sistema

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Navegador web moderno
- Conexão com internet

## 👥 Equipe

**André Rovai Andrade Xavier Junior**  
RM555848@fiap.com.br

**Alan de Souza Maximiano da Silva**  
RM557088@fiap.com.br

**Leonardo Zago Garcia Ferreira**  
RM558691@fiap.com.br

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
