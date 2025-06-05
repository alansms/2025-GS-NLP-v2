"""
Simulador de Dados para o Monitor de Emergências
Gera dados simulados para testes quando a API do Twitter está indisponível ou com rate limit
"""

import pandas as pd
import random
from datetime import datetime, timedelta
import json
import os
import uuid

class SimuladorDados:
    """Classe para gerar dados simulados de emergências para testes"""

    def __init__(self):
        """Inicializa o simulador com dados de exemplo"""
        self.tipos_desastres = [
            "Enchente", "Deslizamento", "Terremoto", "Incêndio",
            "Seca", "Tempestade", "Furacão", "Tsunami"
        ]

        self.niveis_urgencia = ["Alto", "Médio", "Baixo"]

        self.localizacoes = [
            "São Paulo, SP", "Rio de Janeiro, RJ", "Belo Horizonte, MG",
            "Salvador, BA", "Recife, PE", "Fortaleza, CE", "Manaus, AM",
            "Porto Alegre, RS", "Curitiba, PR", "Brasília, DF",
            "Petrópolis, RJ", "Blumenau, SC", "São Sebastião, SP",
            "Angra dos Reis, RJ", "Campos do Jordão, SP"
        ]

        self.templates_mensagens = [
            "Urgente! {tipo} atingindo a região de {local}. Moradores precisam de ajuda!",
            "Alerta de {tipo} em {local}. Autoridades pedem para população evacuar a área.",
            "Situação crítica em {local} devido a {tipo}. Várias famílias desabrigadas.",
            "Precisamos de ajuda em {local}! {tipo} destruiu várias casas na região.",
            "Atenção para quem está em {local}, {tipo} previsto para as próximas horas.",
            "Estamos organizando doações para vítimas do {tipo} em {local}. Ajude!",
            "{tipo} em {local} causa destruição. Bombeiros trabalham nos resgates.",
            "Defesa Civil alerta para risco de {tipo} em {local}. Fiquem atentos!",
            "Voluntários necessários para ajudar vítimas de {tipo} em {local}.",
            "Estradas bloqueadas devido a {tipo} na região de {local}. Evitem a área."
        ]

        self.nomes_usuarios = [
            "DefesaCivilSP", "AlertaRio", "BombeirosMG", "SOSDesastres",
            "MonitorClima", "EmergenciaBR", "AlertaBrasil", "SOSEnchentes",
            "NoticiasDesastres", "VoluntariosEmergencia"
        ]

    def gerar_mensagem_simulada(self):
        """Gera uma mensagem simulada de emergência"""
        tipo = random.choice(self.tipos_desastres)
        local = random.choice(self.localizacoes)
        template = random.choice(self.templates_mensagens)

        return template.format(tipo=tipo, local=local)

    def gerar_dados_simulados(self, num_mensagens=50):
        """Gera um conjunto de dados simulados para teste"""
        dados = []
        agora = datetime.now()

        for i in range(num_mensagens):
            # Data aleatória nas últimas 48 horas
            horas_atras = random.randint(0, 48)
            data_criacao = agora - timedelta(hours=horas_atras)

            # Tipo de desastre aleatório
            tipo_desastre = random.choice(self.tipos_desastres)

            # Nível de urgência aleatório com tendência para tipos críticos
            if tipo_desastre in ["Enchente", "Deslizamento", "Terremoto"]:
                chances_urgencia = [0.6, 0.3, 0.1]  # Alto, Médio, Baixo
            else:
                chances_urgencia = [0.3, 0.4, 0.3]  # Alto, Médio, Baixo

            nivel_urgencia = random.choices(
                self.niveis_urgencia,
                weights=chances_urgencia
            )[0]

            # Gerar sentimento baseado na urgência
            if nivel_urgencia == "Alto":
                sentimento = random.choices(["negativo", "muito negativo"], weights=[0.3, 0.7])[0]
                score_sentimento = -random.uniform(0.6, 1.0)
                score_urgencia = random.uniform(0.7, 1.0)
            elif nivel_urgencia == "Médio":
                sentimento = random.choices(["negativo", "neutro"], weights=[0.7, 0.3])[0]
                score_sentimento = -random.uniform(0.3, 0.6)
                score_urgencia = random.uniform(0.4, 0.7)
            else:
                sentimento = random.choices(["neutro", "negativo"], weights=[0.6, 0.4])[0]
                score_sentimento = -random.uniform(0.1, 0.3)
                score_urgencia = random.uniform(0.1, 0.4)

            # Localizações
            local_principal = random.choice(self.localizacoes)
            localizacoes = [{"texto": local_principal, "tipo": "cidade"}]

            # Adicionar segunda localização ocasionalmente
            if random.random() > 0.7:
                segundo_local = random.choice([loc for loc in self.localizacoes if loc != local_principal])
                localizacoes.append({"texto": segundo_local, "tipo": "cidade"})

            # Gerar texto
            texto = self.gerar_mensagem_simulada()

            # Dados da mensagem
            mensagem = {
                "id": str(uuid.uuid4()),
                "texto": texto,
                "data_criacao": data_criacao.isoformat(),
                "usuario": random.choice(self.nomes_usuarios),
                "tipo_desastre": tipo_desastre,
                "nivel_urgencia": nivel_urgencia,
                "sentimento": sentimento,
                "score_sentimento": score_sentimento,
                "score_urgencia": score_urgencia,
                "localizacoes": localizacoes,
                "telefones": [],
                "pessoas": [],
                "fonte": "simulado",
                "confianca_classificacao": random.uniform(0.7, 0.98),
                "score_completude": random.uniform(0.5, 0.9)
            }

            dados.append(mensagem)

        # Ordenar por data (mais recentes primeiro)
        dados.sort(key=lambda x: x["data_criacao"], reverse=True)

        return pd.DataFrame(dados)

    def salvar_dados_simulados(self, num_mensagens=50, arquivo='data/mensagens_coletadas.json'):
        """Gera e salva dados simulados no arquivo de dados"""
        df = self.gerar_dados_simulados(num_mensagens)

        # Verificar se o diretório existe
        diretorio = os.path.dirname(arquivo)
        if not os.path.exists(diretorio) and diretorio:
            os.makedirs(diretorio, exist_ok=True)

        # Formatar para JSON
        dados_json = {
            'mensagens': df.to_dict('records'),
            'ultima_atualizacao': datetime.now().isoformat()
        }

        # Salvar arquivo
        with open(arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados_json, f, ensure_ascii=False, indent=2)

        return df

# Exemplo de uso
if __name__ == "__main__":
    simulador = SimuladorDados()
    df = simulador.salvar_dados_simulados(50)
    print(f"✅ {len(df)} mensagens simuladas foram geradas e salvas!")
