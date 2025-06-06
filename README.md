# 🚨 Monitor de Emergências – Sistema Inteligente de Monitoramento em Tempo Real

Sistema inteligente de monitoramento, classificação e análise de mensagens emergenciais sobre desastres naturais. Desenvolvido como parte da Global Solution da FIAP.

---

## 🎯 Visão Geral

Este projeto implementa um sistema completo para rastreamento e análise de desastres naturais em tempo real. Ele realiza:

- Coleta de dados por meio da **Serper API**, com foco em notícias emergenciais
- Análise de linguagem natural (NLP) para extração de entidades e sentimentos
- Classificação automática de tipos de desastre (enchente, incêndio, terremoto etc.)
- Estimativa de urgência com sistema de pontuação
- Visualizações gráficas, mapas interativos e alertas em tempo real

---

## 🌐 Acesse a Aplicação

https://2025-gs-nlp-v2-nbuhmg6qb6xctv94aqrszf.streamlit.app


![Demonstração do Frontend](https://raw.githubusercontent.com/alansms/2025-GS-NLP-v2/main/2025-GS-NLP/img/app.gif)

---

## 📄 Relatório do Projeto

[![Ver Relatório (PDF)](https://img.shields.io/badge/Acessar%20Relat%C3%B3rio-PDF-red?logo=adobeacrobatreader&logoColor=white)](https://github.com/alansms/2025-GS-NLP-v2/raw/main/2025-GS-NLP/img/Relato%CC%81rio%20Resumido%20-%20Monitoramento%20de%20Emerge%CC%82ncias.pdf)

---

## 🛠️ Tecnologias Utilizadas

| Camada        | Tecnologias principais |
|---------------|------------------------|
| **Frontend**  | Streamlit              |
| **Backend**   | Python 3.11+, Pandas, Numpy |
| **NLP**       | spaCy, Hugging Face Transformers, VADER, TextBlob |
| **ML**        | Scikit-learn           |
| **Visualização** | Plotly, Matplotlib, WordCloud, Folium |
| **Integração de Dados** | Serper.dev API, Tweepy (Twitter API) |

---

## 🚀 Como Executar Localmente

1. Clone o repositório:

```bash
git clone https://github.com/alansms/2025-GS-NLP-v2.git
cd 2025-GS-NLP-v2
```

2. Crie o ambiente e instale as dependências:

```bash
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure sua API Key da Serper (https://serper.dev/)

4. Execute o app:

```bash
streamlit run app.py
```

---

## 📊 Funcionalidades do Sistema

### 📍 Dashboard Principal
- Métricas em tempo real
- Gráficos interativos e visualização temporal
- Filtros por tipo de desastre, urgência e período

### 🧠 Processamento NLP
- Classificação automática de tipos de desastres
- Análise de sentimento e extração de entidades
- Estimativa de urgência baseada em regras

### 🗺️ Visualizações Geográficas
- Mapa interativo com marcadores por cidade
- Nuvem de palavras dinâmicas
- Camadas de calor e agrupamento de emergências

### 🚨 Sistema de Alerta
- Detecção automática de eventos críticos
- Classificação de mensagens por criticidade
- Atualização periódica automatizada

---

## 📁 Estrutura do Projeto

```
2025-GS-NLP/
├── app.py                    # Aplicação principal
├── nlp/                      # Módulos de NLP e classificação
│   ├── analise_sentimento.py
│   ├── classificador_tipo.py
│   └── extrator_entidades.py
├── visuals/                  # Visualizações (mapa, nuvem, gráficos)
│   ├── mapa.py
│   └── wordcloud_gen.py
├── data/                     # Arquivos JSON processados
├── config/                   # Arquivos de configuração e tokens
```

---

## 📌 Requisitos

- Python 3.11 ou superior
- Navegador moderno
- Conexão com internet (para APIs externas)

---

## 👥 Equipe

- **André Rovai Andrade Xavier Junior** – RM555848@fiap.com.br  
- **Alan de Souza Maximiano da Silva** – RM557088@fiap.com.br  
- **Leonardo Zago Garcia Ferreira** – RM558691@fiap.com.br

---

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para mais detalhes.
