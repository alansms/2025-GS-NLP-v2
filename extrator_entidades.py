"""
Módulo de Extração de Entidades para Mensagens de Emergência
Utiliza spaCy para identificar pessoas, localizações, telefones e informações críticas
"""

import re
import spacy
from typing import Dict, List, Tuple, Set
import pandas as pd
from collections import defaultdict


class ExtratorEntidades:
    """Classe para extração de entidades nomeadas e informações críticas"""
    
    def __init__(self, modelo_spacy='pt_core_news_sm'):
        """
        Inicializa o extrator de entidades
        
        Args:
            modelo_spacy (str): Nome do modelo spaCy para português
        """
        try:
            self.nlp = spacy.load(modelo_spacy)
        except OSError:
            print(f"Modelo {modelo_spacy} não encontrado. Tentando carregar modelo alternativo...")
            try:
                # Tenta carregar modelo menor se disponível
                self.nlp = spacy.load('pt_core_news_md')
            except OSError:
                print("Nenhum modelo português encontrado. Usando modelo em inglês como fallback.")
                self.nlp = spacy.load('en_core_web_sm')
        
        # Padrões regex para diferentes tipos de informação
        self.padroes = {
            'telefone': [
                r'\b(?:\+55\s?)?(?:\(?0?(?:11|12|13|14|15|16|17|18|19|21|22|24|27|28|31|32|33|34|35|37|38|41|42|43|44|45|46|47|48|49|51|53|54|55|61|62|63|64|65|66|67|68|69|71|73|74|75|77|79|81|82|83|84|85|86|87|88|89|91|92|93|94|95|96|97|98|99)\)?\s?)?(?:9\s?)?[0-9]{4}[-\s]?[0-9]{4}\b',
                r'\b(?:190|192|193|199|911)\b',  # Números de emergência
            ],
            'cep': r'\b\d{5}-?\d{3}\b',
            'endereco_numero': r'\b(?:rua|av|avenida|travessa|alameda|praça|largo)\s+[^,\n]+(?:,\s*)?(?:n[°º]?\s*)?(\d+)',
            'coordenadas': r'-?\d{1,2}\.\d+,\s*-?\d{1,2}\.\d+',
            'horario': r'\b(?:[01]?[0-9]|2[0-3]):[0-5][0-9](?::[0-5][0-9])?\b',
            'data': r'\b(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{2,4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b'
        }
        
        # Palavras-chave para contexto de emergência
        self.contextos_emergencia = {
            'pessoas_vulneraveis': [
                'criança', 'crianças', 'bebê', 'bebês', 'idoso', 'idosos', 'idosa', 'idosas',
                'gestante', 'grávida', 'deficiente', 'cadeirante', 'doente', 'ferido', 'ferida'
            ],
            'locais_risco': [
                'ponte', 'viaduto', 'túnel', 'encosta', 'morro', 'barranco', 'córrego',
                'rio', 'represa', 'açude', 'escola', 'hospital', 'creche', 'asilo'
            ],
            'situacoes_criticas': [
                'preso', 'presa', 'ilhado', 'ilhada', 'soterrado', 'soterrada',
                'desaparecido', 'desaparecida', 'perdido', 'perdida', 'ferido', 'ferida'
            ]
        }
        
        # Lista de cidades brasileiras comuns (amostra)
        self.cidades_brasileiras = {
            'são paulo', 'rio de janeiro', 'belo horizonte', 'salvador', 'brasília',
            'fortaleza', 'manaus', 'curitiba', 'recife', 'porto alegre', 'goiânia',
            'belém', 'guarulhos', 'campinas', 'são luís', 'maceió', 'natal',
            'teresina', 'campo grande', 'joão pessoa', 'jaboatão dos guararapes',
            'osasco', 'santo andré', 'são bernardo do campo', 'contagem', 'uberlândia'
        }
    
    def extrair_telefones(self, texto: str) -> List[Dict]:
        """
        Extrai números de telefone do texto
        
        Args:
            texto (str): Texto para análise
            
        Returns:
            List[Dict]: Lista de telefones encontrados
        """
        telefones = []
        
        for padrao in self.padroes['telefone']:
            matches = re.finditer(padrao, texto, re.IGNORECASE)
            for match in matches:
                telefone = match.group().strip()
                # Limpa formatação
                telefone_limpo = re.sub(r'[^\d+]', '', telefone)
                
                # Classifica tipo de telefone
                if telefone_limpo in ['190', '192', '193', '199', '911']:
                    tipo = 'emergencia'
                elif len(telefone_limpo) >= 10:
                    tipo = 'celular' if '9' in telefone_limpo[2:4] else 'fixo'
                else:
                    tipo = 'desconhecido'
                
                telefones.append({
                    'numero': telefone,
                    'numero_limpo': telefone_limpo,
                    'tipo': tipo,
                    'posicao': match.span()
                })
        
        return telefones
    
    def extrair_localizacoes(self, texto: str) -> List[Dict]:
        """
        Extrai informações de localização do texto
        
        Args:
            texto (str): Texto para análise
            
        Returns:
            List[Dict]: Lista de localizações encontradas
        """
        doc = self.nlp(texto)
        localizacoes = []
        
        # Entidades nomeadas de localização via spaCy
        for ent in doc.ents:
            if ent.label_ in ['LOC', 'GPE', 'MISC']:  # Localização, entidade geopolítica
                localizacoes.append({
                    'texto': ent.text,
                    'tipo': 'entidade_nomeada',
                    'label': ent.label_,
                    'posicao': (ent.start_char, ent.end_char),
                    'confianca': 'alta'
                })
        
        # CEPs
        ceps = re.finditer(self.padroes['cep'], texto)
        for match in ceps:
            localizacoes.append({
                'texto': match.group(),
                'tipo': 'cep',
                'label': 'CEP',
                'posicao': match.span(),
                'confianca': 'alta'
            })
        
        # Coordenadas geográficas
        coords = re.finditer(self.padroes['coordenadas'], texto)
        for match in coords:
            localizacoes.append({
                'texto': match.group(),
                'tipo': 'coordenadas',
                'label': 'COORD',
                'posicao': match.span(),
                'confianca': 'alta'
            })
        
        # Endereços com números
        enderecos = re.finditer(self.padroes['endereco_numero'], texto, re.IGNORECASE)
        for match in enderecos:
            localizacoes.append({
                'texto': match.group(),
                'tipo': 'endereco',
                'label': 'ENDERECO',
                'posicao': match.span(),
                'confianca': 'média'
            })
        
        # Cidades brasileiras conhecidas
        texto_lower = texto.lower()
        for cidade in self.cidades_brasileiras:
            if cidade in texto_lower:
                inicio = texto_lower.find(cidade)
                fim = inicio + len(cidade)
                localizacoes.append({
                    'texto': texto[inicio:fim],
                    'tipo': 'cidade',
                    'label': 'CIDADE',
                    'posicao': (inicio, fim),
                    'confianca': 'média'
                })
        
        return localizacoes
    
    def extrair_pessoas(self, texto: str) -> List[Dict]:
        """
        Extrai informações sobre pessoas mencionadas
        
        Args:
            texto (str): Texto para análise
            
        Returns:
            List[Dict]: Lista de pessoas encontradas
        """
        doc = self.nlp(texto)
        pessoas = []
        
        # Entidades nomeadas de pessoa via spaCy
        for ent in doc.ents:
            if ent.label_ in ['PER', 'PERSON']:
                pessoas.append({
                    'nome': ent.text,
                    'tipo': 'nome_proprio',
                    'posicao': (ent.start_char, ent.end_char),
                    'contexto': self._extrair_contexto(texto, ent.start_char, ent.end_char)
                })
        
        # Pessoas vulneráveis mencionadas
        for categoria, palavras in self.contextos_emergencia.items():
            if categoria == 'pessoas_vulneraveis':
                for palavra in palavras:
                    pattern = r'\b' + re.escape(palavra) + r'\b'
                    matches = re.finditer(pattern, texto, re.IGNORECASE)
                    for match in matches:
                        pessoas.append({
                            'nome': match.group(),
                            'tipo': 'pessoa_vulneravel',
                            'categoria': palavra,
                            'posicao': match.span(),
                            'contexto': self._extrair_contexto(texto, match.start(), match.end())
                        })
        
        return pessoas
    
    def extrair_informacoes_temporais(self, texto: str) -> List[Dict]:
        """
        Extrai informações de data e hora
        
        Args:
            texto (str): Texto para análise
            
        Returns:
            List[Dict]: Lista de informações temporais
        """
        temporais = []
        
        # Horários
        horarios = re.finditer(self.padroes['horario'], texto)
        for match in horarios:
            temporais.append({
                'texto': match.group(),
                'tipo': 'horario',
                'posicao': match.span()
            })
        
        # Datas
        datas = re.finditer(self.padroes['data'], texto)
        for match in datas:
            temporais.append({
                'texto': match.group(),
                'tipo': 'data',
                'posicao': match.span()
            })
        
        # Expressões temporais via spaCy
        doc = self.nlp(texto)
        for ent in doc.ents:
            if ent.label_ in ['DATE', 'TIME']:
                temporais.append({
                    'texto': ent.text,
                    'tipo': 'expressao_temporal',
                    'label': ent.label_,
                    'posicao': (ent.start_char, ent.end_char)
                })
        
        return temporais
    
    def extrair_situacoes_criticas(self, texto: str) -> List[Dict]:
        """
        Identifica situações críticas mencionadas
        
        Args:
            texto (str): Texto para análise
            
        Returns:
            List[Dict]: Lista de situações críticas
        """
        situacoes = []
        
        for categoria, palavras in self.contextos_emergencia.items():
            for palavra in palavras:
                pattern = r'\b' + re.escape(palavra) + r'\b'
                matches = re.finditer(pattern, texto, re.IGNORECASE)
                for match in matches:
                    situacoes.append({
                        'situacao': match.group(),
                        'categoria': categoria,
                        'posicao': match.span(),
                        'contexto': self._extrair_contexto(texto, match.start(), match.end())
                    })
        
        return situacoes
    
    def _extrair_contexto(self, texto: str, inicio: int, fim: int, janela: int = 50) -> str:
        """
        Extrai contexto ao redor de uma entidade
        
        Args:
            texto (str): Texto completo
            inicio (int): Posição inicial da entidade
            fim (int): Posição final da entidade
            janela (int): Tamanho da janela de contexto
            
        Returns:
            str: Contexto extraído
        """
        inicio_contexto = max(0, inicio - janela)
        fim_contexto = min(len(texto), fim + janela)
        return texto[inicio_contexto:fim_contexto].strip()
    
    def extrair_todas_entidades(self, texto: str) -> Dict:
        """
        Extrai todas as entidades de uma mensagem
        
        Args:
            texto (str): Texto da mensagem
            
        Returns:
            Dict: Todas as entidades extraídas
        """
        resultado = {
            'texto_original': texto,
            'telefones': self.extrair_telefones(texto),
            'localizacoes': self.extrair_localizacoes(texto),
            'pessoas': self.extrair_pessoas(texto),
            'informacoes_temporais': self.extrair_informacoes_temporais(texto),
            'situacoes_criticas': self.extrair_situacoes_criticas(texto)
        }
        
        # Calcula score de completude da informação
        score_completude = 0
        if resultado['telefones']:
            score_completude += 3
        if resultado['localizacoes']:
            score_completude += 4
        if resultado['pessoas']:
            score_completude += 2
        if resultado['informacoes_temporais']:
            score_completude += 1
        if resultado['situacoes_criticas']:
            score_completude += 2
        
        resultado['score_completude'] = min(score_completude, 10)
        
        return resultado
    
    def processar_lote(self, mensagens: List[str]) -> pd.DataFrame:
        """
        Processa um lote de mensagens
        
        Args:
            mensagens (List[str]): Lista de mensagens
            
        Returns:
            pd.DataFrame: DataFrame com entidades extraídas
        """
        resultados = []
        
        for i, mensagem in enumerate(mensagens):
            try:
                resultado = self.extrair_todas_entidades(mensagem)
                resultado['id_mensagem'] = i
                resultados.append(resultado)
            except Exception as e:
                print(f"Erro ao processar mensagem {i}: {e}")
                continue
        
        return pd.DataFrame(resultados)
    
    def obter_estatisticas_entidades(self, df_entidades: pd.DataFrame) -> Dict:
        """
        Calcula estatísticas das entidades extraídas
        
        Args:
            df_entidades (pd.DataFrame): DataFrame com entidades
            
        Returns:
            Dict: Estatísticas
        """
        if df_entidades.empty:
            return {}
        
        stats = {
            'total_mensagens': len(df_entidades),
            'mensagens_com_telefone': len(df_entidades[df_entidades['telefones'].apply(len) > 0]),
            'mensagens_com_localizacao': len(df_entidades[df_entidades['localizacoes'].apply(len) > 0]),
            'mensagens_com_pessoas': len(df_entidades[df_entidades['pessoas'].apply(len) > 0]),
            'score_completude_medio': df_entidades['score_completude'].mean(),
            'total_telefones': sum(len(tel) for tel in df_entidades['telefones']),
            'total_localizacoes': sum(len(loc) for loc in df_entidades['localizacoes']),
            'situacoes_criticas_mais_comuns': self._contar_situacoes_criticas(df_entidades)
        }
        
        return stats
    
    def _contar_situacoes_criticas(self, df: pd.DataFrame) -> Dict:
        """
        Conta situações críticas mais comuns
        
        Args:
            df (pd.DataFrame): DataFrame com dados
            
        Returns:
            Dict: Contagem de situações
        """
        contagem = defaultdict(int)
        
        for situacoes in df['situacoes_criticas']:
            for situacao in situacoes:
                contagem[situacao['situacao']] += 1
        
        return dict(sorted(contagem.items(), key=lambda x: x[1], reverse=True)[:10])


# Função de conveniência
def extrair_entidades_rapido(texto: str) -> Dict:
    """
    Função de conveniência para extração rápida
    
    Args:
        texto (str): Texto para análise
        
    Returns:
        Dict: Entidades extraídas
    """
    extrator = ExtratorEntidades()
    return extrator.extrair_todas_entidades(texto)


if __name__ == "__main__":
    # Teste do módulo
    mensagens_teste = [
        "Socorro! Estou preso na Rua das Flores, 123 com minha filha de 5 anos. Ligue 11 99999-9999",
        "Incêndio na Avenida Paulista próximo ao hospital. Idosos precisam de evacuação urgente",
        "Criança desaparecida na região do CEP 01310-100. Contato: (11) 98765-4321",
        "Deslizamento na encosta do Morro da Esperança às 14:30. Várias pessoas soterradas",
        "Enchente na ponte do Rio Tietê. Coordenadas: -23.5505, -46.6333"
    ]
    
    print("=== Teste do Extrator de Entidades ===")
    
    extrator = ExtratorEntidades()
    
    for i, msg in enumerate(mensagens_teste):
        print(f"\n--- Mensagem {i+1} ---")
        print(f"Texto: {msg}")
        
        resultado = extrator.extrair_todas_entidades(msg)
        
        print(f"Score de completude: {resultado['score_completude']}/10")
        
        if resultado['telefones']:
            print(f"Telefones: {[tel['numero'] for tel in resultado['telefones']]}")
        
        if resultado['localizacoes']:
            print(f"Localizações: {[loc['texto'] for loc in resultado['localizacoes']]}")
        
        if resultado['pessoas']:
            print(f"Pessoas: {[p['nome'] for p in resultado['pessoas']]}")
        
        if resultado['situacoes_criticas']:
            print(f"Situações críticas: {[s['situacao'] for s in resultado['situacoes_criticas']]}")
    
    # Teste em lote
    df_resultados = extrator.processar_lote(mensagens_teste)
    stats = extrator.obter_estatisticas_entidades(df_resultados)
    
    print("\n--- Estatísticas Gerais ---")
    print(f"Total de mensagens: {stats['total_mensagens']}")
    print(f"Mensagens com telefone: {stats['mensagens_com_telefone']}")
    print(f"Mensagens com localização: {stats['mensagens_com_localizacao']}")
    print(f"Score médio de completude: {stats['score_completude_medio']:.2f}")
    print(f"Total de telefones: {stats['total_telefones']}")
    print(f"Total de localizações: {stats['total_localizacoes']}")

