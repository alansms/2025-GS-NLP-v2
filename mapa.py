"""
Módulo de Mapa Interativo para Emergências
Cria mapas interativos com localizações de emergências usando Folium
"""

import folium
from folium import plugins
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
import json
import re
from datetime import datetime, timedelta


class GeradorMapaEmergencia:
    """Classe para geração de mapas interativos de emergências"""
    
    def __init__(self, centro_brasil: Tuple[float, float] = (-14.2350, -51.9253)):
        """
        Inicializa o gerador de mapas
        
        Args:
            centro_brasil (Tuple[float, float]): Coordenadas do centro do Brasil
        """
        self.centro_brasil = centro_brasil
        
        # Cores por tipo de emergência
        self.cores_emergencia = {
            'enchente': '#1E90FF',      # Azul
            'incendio': '#FF4500',      # Laranja avermelhado
            'deslizamento': '#8B4513',  # Marrom
            'vendaval': '#708090',      # Cinza ardósia
            'granizo': '#E6E6FA',       # Lavanda
            'terremoto': '#A0522D',     # Marrom claro
            'acidente': '#FF0000',      # Vermelho
            'emergencia_medica': '#00FF00', # Verde
            'outros': '#808080'         # Cinza
        }
        
        # Ícones por tipo de emergência
        self.icones_emergencia = {
            'enchente': 'tint',
            'incendio': 'fire',
            'deslizamento': 'exclamation-triangle',
            'vendaval': 'wind',
            'granizo': 'cloud',
            'terremoto': 'warning',
            'acidente': 'car',
            'emergencia_medica': 'plus',
            'outros': 'info'
        }
        
        # Coordenadas aproximadas de cidades brasileiras principais
        self.coordenadas_cidades = {
            'são paulo': (-23.5505, -46.6333),
            'rio de janeiro': (-22.9068, -43.1729),
            'belo horizonte': (-19.9167, -43.9345),
            'salvador': (-12.9714, -38.5014),
            'brasília': (-15.8267, -47.9218),
            'fortaleza': (-3.7319, -38.5267),
            'manaus': (-3.1190, -60.0217),
            'curitiba': (-25.4244, -49.2654),
            'recife': (-8.0476, -34.8770),
            'porto alegre': (-30.0346, -51.2177),
            'goiânia': (-16.6869, -49.2648),
            'belém': (-1.4558, -48.5044),
            'guarulhos': (-23.4538, -46.5333),
            'campinas': (-22.9099, -47.0626),
            'são luís': (-2.5387, -44.2825),
            'maceió': (-9.6658, -35.7353),
            'natal': (-5.7945, -35.2110),
            'teresina': (-5.0892, -42.8019),
            'campo grande': (-20.4697, -54.6201),
            'joão pessoa': (-7.1195, -34.8450)
        }
    
    def extrair_coordenadas_texto(self, texto: str) -> Optional[Tuple[float, float]]:
        """
        Extrai coordenadas geográficas do texto
        
        Args:
            texto (str): Texto da mensagem
            
        Returns:
            Optional[Tuple[float, float]]: Coordenadas (lat, lon) ou None
        """
        # Padrão para coordenadas (latitude, longitude)
        padrao_coords = r'(-?\d{1,2}\.\d+),\s*(-?\d{1,2}\.\d+)'
        match = re.search(padrao_coords, texto)
        
        if match:
            lat, lon = float(match.group(1)), float(match.group(2))
            # Verifica se as coordenadas são válidas para o Brasil
            if -35 <= lat <= 5 and -75 <= lon <= -30:
                return (lat, lon)
        
        return None
    
    def geocodificar_cidade(self, texto: str) -> Optional[Tuple[float, float]]:
        """
        Tenta encontrar coordenadas baseadas em nomes de cidades
        
        Args:
            texto (str): Texto da mensagem
            
        Returns:
            Optional[Tuple[float, float]]: Coordenadas (lat, lon) ou None
        """
        texto_lower = texto.lower()
        
        for cidade, coords in self.coordenadas_cidades.items():
            if cidade in texto_lower:
                return coords
        
        return None
    
    def processar_localizacoes(self, dados: pd.DataFrame,
                              coluna_texto: str = 'texto',
                              coluna_tipo: str = 'tipo_desastre',
                              coluna_urgencia: str = 'nivel_urgencia') -> pd.DataFrame:
        """
        Processa DataFrame para extrair localiza��ões

        Args:
            dados (pd.DataFrame): DataFrame com dados
            coluna_texto (str): Nome da coluna com texto
            coluna_tipo (str): Nome da coluna com tipo de emergência
            coluna_urgencia (str): Nome da coluna com nível de urgência
            
        Returns:
            pd.DataFrame: DataFrame com localizações processadas
        """
        # Verifica se o DataFrame está vazio
        if dados.empty:
            print("Aviso: DataFrame vazio passado para processar_localizacoes")
            return pd.DataFrame()
            
        dados_com_coords = []
        
        for idx, row in dados.iterrows():
            texto = row[coluna_texto]
            
            # Tenta extrair coordenadas do texto
            coords = self.extrair_coordenadas_texto(texto)
            
            # Se não encontrou, tenta geocodificar por cidade
            if not coords:
                coords = self.geocodificar_cidade(texto)
            
            # Se ainda não encontrou, usa coordenadas aleatórias próximas ao centro do Brasil
            if not coords:
                # Gera coordenadas aleatórias em um raio de ~500km do centro do Brasil
                lat_offset = np.random.uniform(-5, 5)
                lon_offset = np.random.uniform(-5, 5)
                coords = (self.centro_brasil[0] + lat_offset, 
                         self.centro_brasil[1] + lon_offset)
            
            # Adiciona dados processados
            dados_processados = row.to_dict()
            dados_processados['latitude'] = coords[0]
            dados_processados['longitude'] = coords[1]
            dados_processados['coords_origem'] = 'extraida' if self.extrair_coordenadas_texto(texto) else \
                                               'geocodificada' if self.geocodificar_cidade(texto) else 'estimada'
            
            dados_com_coords.append(dados_processados)
        
        return pd.DataFrame(dados_com_coords)
    
    def criar_mapa_base(self, centro: Optional[Tuple[float, float]] = None,
                       zoom_inicial: int = 5) -> folium.Map:
        """
        Cria mapa base
        
        Args:
            centro (Tuple[float, float], optional): Centro do mapa
            zoom_inicial (int): Nível de zoom inicial
            
        Returns:
            folium.Map: Mapa base
        """
        centro = centro or self.centro_brasil
        
        mapa = folium.Map(
            location=centro,
            zoom_start=zoom_inicial,
            tiles='OpenStreetMap'
        )
        
        # Adiciona controle de camadas
        folium.LayerControl().add_to(mapa)
        
        return mapa
    
    def adicionar_marcadores_emergencia(self, mapa: folium.Map, 
                                       dados: pd.DataFrame,
                                       mostrar_popup: bool = True,
                                       agrupar_marcadores: bool = True) -> folium.Map:
        """
        Adiciona marcadores de emergência ao mapa
        
        Args:
            mapa (folium.Map): Mapa base
            dados (pd.DataFrame): Dados com localizações
            mostrar_popup (bool): Se deve mostrar popup nos marcadores
            agrupar_marcadores (bool): Se deve agrupar marcadores próximos
            
        Returns:
            folium.Map: Mapa com marcadores
        """
        if dados.empty:
            return mapa
        
        # Cria grupo de marcadores se solicitado
        if agrupar_marcadores:
            marker_cluster = plugins.MarkerCluster().add_to(mapa)
            container = marker_cluster
        else:
            container = mapa
        
        for idx, row in dados.iterrows():
            # Determina cor e ícone baseado no tipo
            tipo = row.get('tipo_desastre', 'outros')
            cor = self.cores_emergencia.get(tipo, '#808080')
            icone = self.icones_emergencia.get(tipo, 'info')
            
            # Determina tamanho baseado na urgência
            urgencia = row.get('nivel_urgencia', 'baixa')
            if urgencia == 'crítica':
                tamanho = 'large'
            elif urgencia == 'alta':
                tamanho = 'medium'
            else:
                tamanho = 'small'
            
            # Cria popup se solicitado
            popup_html = None
            if mostrar_popup:
                popup_html = self._criar_popup_emergencia(row)
            
            # Determina cor do marcador baseado no tipo de desastre
            # Mapeia as cores personalizadas para as cores padrão do Folium
            cor_folium = 'blue'  # cor padrão
            if tipo == 'enchente' or tipo == 'Enchente':
                cor_folium = 'blue'
            elif tipo == 'incendio' or tipo == 'Incêndio':
                cor_folium = 'red'
            elif tipo == 'deslizamento' or tipo == 'Deslizamento':
                cor_folium = 'darkred'
            elif tipo == 'vendaval' or tipo == 'Vendaval':
                cor_folium = 'gray'
            elif tipo == 'granizo' or tipo == 'Granizo':
                cor_folium = 'lightblue'
            elif tipo == 'terremoto' or tipo == 'Terremoto':
                cor_folium = 'darkpurple'
            elif tipo == 'acidente' or tipo == 'Acidente':
                cor_folium = 'orange'
            elif tipo == 'emergencia_medica' or tipo == 'Emergência Médica':
                cor_folium = 'green'
            elif tipo == 'seca' or tipo == 'Seca':
                cor_folium = 'beige'

            # Adicionar borda mais forte para urgências críticas
            extra_options = {}
            if urgencia == 'crítica':
                extra_options = {"className": "fa-2x"}

            # Adiciona marcador
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=popup_html,
                tooltip=f"{tipo.title()} - {urgencia.title()}",
                icon=folium.Icon(
                    color=cor_folium,
                    icon=icone,
                    prefix='fa',
                    **extra_options
                )
            ).add_to(container)
        
        return mapa
    
    def _criar_popup_emergencia(self, dados_emergencia: pd.Series) -> str:
        """
        Cria HTML para popup de emergência
        
        Args:
            dados_emergencia (pd.Series): Dados da emergência
            
        Returns:
            str: HTML do popup
        """
        texto = dados_emergencia.get('texto', 'Sem descrição')[:200] + "..."
        tipo = dados_emergencia.get('tipo_desastre', 'Não classificado').title()
        urgencia = dados_emergencia.get('nivel_urgencia', 'Não avaliada').title()
        data = dados_emergencia.get('data_criacao', 'Data não disponível')
        coords_origem = dados_emergencia.get('coords_origem', 'desconhecida')
        
        # Formata data se disponível
        try:
            if isinstance(data, str) and data != 'Data não disponível':
                data_obj = datetime.fromisoformat(data.replace('Z', '+00:00'))
                data_formatada = data_obj.strftime('%d/%m/%Y %H:%M')
            else:
                data_formatada = data
        except:
            data_formatada = data
        
        html = f"""
        <div style="width: 300px;">
            <h4 style="color: {self.cores_emergencia.get(dados_emergencia.get('tipo_desastre', 'outros'), '#000')};">
                <i class="fa fa-exclamation-triangle" style="color: red;"></i> {tipo}
            </h4>
            <p><strong>Urgência:</strong> 
                <span style="color: {'red' if urgencia == 'Crítica' else 'orange' if urgencia == 'Alta' else 'blue'};">
                    <i class="fa fa-circle" style="color: {'red' if urgencia == 'Crítica' else 'orange' if urgencia == 'Alta' else 'blue'};"></i> {urgencia}
                </span>
            </p>
            <p><strong>Descrição:</strong><br>{texto}</p>
            <p><strong>Data:</strong> {data_formatada}</p>
            <p><strong>Localização:</strong> {coords_origem.title()}</p>
            <hr>
            <small>Coordenadas: {dados_emergencia.get('latitude', 0):.4f}, {dados_emergencia.get('longitude', 0):.4f}</small>
        </div>
        """
        
        return html
    
    def adicionar_mapa_calor(self, mapa: folium.Map, dados: pd.DataFrame,
                           raio: int = 15, blur: int = 15) -> folium.Map:
        """
        Adiciona mapa de calor das emergências
        
        Args:
            mapa (folium.Map): Mapa base
            dados (pd.DataFrame): Dados com localizações
            raio (int): Raio dos pontos no mapa de calor
            blur (int): Blur dos pontos
            
        Returns:
            folium.Map: Mapa com camada de calor
        """
        if dados.empty:
            return mapa
        
        # Prepara dados para mapa de calor
        pontos_calor = []
        for idx, row in dados.iterrows():
            # Peso baseado na urgência
            urgencia = row.get('nivel_urgencia', 'baixa')
            if urgencia == 'crítica':
                peso = 1.0
            elif urgencia == 'alta':
                peso = 0.7
            elif urgencia == 'média':
                peso = 0.5
            else:
                peso = 0.3
            
            pontos_calor.append([row['latitude'], row['longitude'], peso])
        
        # Adiciona mapa de calor
        plugins.HeatMap(
            pontos_calor,
            radius=raio,
            blur=blur,
            max_zoom=1,
            name='Densidade de Emergências'
        ).add_to(mapa)
        
        return mapa
    
    def criar_mapa_temporal(self, dados: pd.DataFrame,
                           coluna_data: str = 'data_criacao',
                           intervalo_horas: int = 6) -> folium.Map:
        """
        Cria mapa com animação temporal das emergências
        
        Args:
            dados (pd.DataFrame): Dados com localizações e datas
            coluna_data (str): Nome da coluna com datas
            intervalo_horas (int): Intervalo em horas para agrupamento
            
        Returns:
            folium.Map: Mapa com animação temporal
        """
        if dados.empty:
            return self.criar_mapa_base()
        
        # Converte datas
        dados = dados.copy()
        dados[coluna_data] = pd.to_datetime(dados[coluna_data])
        
        # Agrupa por intervalos de tempo
        dados['periodo'] = dados[coluna_data].dt.floor(f'{intervalo_horas}H')
        
        # Cria mapa base
        mapa = self.criar_mapa_base()
        
        # Prepara dados para TimestampedGeoJson
        features = []
        for periodo, grupo in dados.groupby('periodo'):
            for idx, row in grupo.iterrows():
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [row['longitude'], row['latitude']]
                    },
                    "properties": {
                        "time": periodo.isoformat(),
                        "popup": self._criar_popup_emergencia(row),
                        "icon": "marker",
                        "iconstyle": {
                            "color": self.cores_emergencia.get(row.get('tipo_desastre', 'outros'), '#808080'),
                            "fillColor": self.cores_emergencia.get(row.get('tipo_desastre', 'outros'), '#808080'),
                            "fillOpacity": 0.8
                        }
                    }
                }
                features.append(feature)
        
        # Adiciona animação temporal
        if features:
            plugins.TimestampedGeoJson(
                {
                    "type": "FeatureCollection",
                    "features": features
                },
                period="PT{}H".format(intervalo_horas),
                add_last_point=True,
                auto_play=False,
                loop=False,
                max_speed=2,
                loop_button=True,
                date_options="YYYY-MM-DD HH:mm",
                time_slider_drag_update=True
            ).add_to(mapa)
        
        return mapa
    
    def adicionar_areas_risco(self, mapa: folium.Map, 
                             areas_risco: List[Dict]) -> folium.Map:
        """
        Adiciona áreas de risco ao mapa
        
        Args:
            mapa (folium.Map): Mapa base
            areas_risco (List[Dict]): Lista de áreas de risco
            
        Returns:
            folium.Map: Mapa com áreas de risco
        """
        for area in areas_risco:
            # Cria polígono da área de risco
            folium.Polygon(
                locations=area['coordenadas'],
                popup=f"Área de Risco: {area['nome']}",
                tooltip=f"Risco: {area['tipo_risco']}",
                color=area.get('cor', 'red'),
                weight=2,
                fillColor=area.get('cor', 'red'),
                fillOpacity=0.3
            ).add_to(mapa)
        
        return mapa
    
    def gerar_estatisticas_mapa(self, dados: pd.DataFrame) -> Dict:
        """
        Gera estatísticas para o mapa
        
        Args:
            dados (pd.DataFrame): Dados processados
            
        Returns:
            Dict: Estatísticas do mapa
        """
        # Verifica se o DataFrame está vazio
        if dados is None or dados.empty:
            return {}
        
        stats = {
            'total_emergencias': len(dados),
            'por_tipo': dados['tipo_desastre'].value_counts().to_dict() if 'tipo_desastre' in dados.columns else {},
            'por_urgencia': dados['nivel_urgencia'].value_counts().to_dict() if 'nivel_urgencia' in dados.columns else {},
            'coordenadas_extraidas': len(dados[dados['coords_origem'] == 'extraida']) if 'coords_origem' in dados.columns else 0,
            'coordenadas_geocodificadas': len(dados[dados['coords_origem'] == 'geocodificada']) if 'coords_origem' in dados.columns else 0,
            'coordenadas_estimadas': len(dados[dados['coords_origem'] == 'estimada']) if 'coords_origem' in dados.columns else 0,
            'centro_massa': (dados['latitude'].mean(), dados['longitude'].mean()),
            'bbox': {
                'norte': dados['latitude'].max(),
                'sul': dados['latitude'].min(),
                'leste': dados['longitude'].max(),
                'oeste': dados['longitude'].min()
            }
        }
        
        return stats
    
    def salvar_mapa(self, mapa: folium.Map, arquivo: str):
        """
        Salva mapa em arquivo HTML
        
        Args:
            mapa (folium.Map): Mapa a ser salvo
            arquivo (str): Caminho do arquivo
        """
        mapa.save(arquivo)

    def gerar_mapa(self, dados: pd.DataFrame) -> folium.Map:
        """
        Gera um mapa completo com todas as emergências

        Args:
            dados (pd.DataFrame): DataFrame com dados de emergências

        Returns:
            folium.Map: Mapa completo com marcadores
        """
        # Verifica se o DataFrame está vazio
        if dados.empty:
            return self.criar_mapa_base()

        # Verifica se há coordenadas no DataFrame
        if 'latitude' not in dados.columns or 'longitude' not in dados.columns:
            raise ValueError("DataFrame não contém coordenadas (latitude/longitude)")

        # Calcula centro do mapa baseado na média das coordenadas
        try:
            lat_media = dados['latitude'].mean()
            lon_media = dados['longitude'].mean()
            centro = (lat_media, lon_media)
        except:
            # Se falhar, usa o centro do Brasil
            centro = self.centro_brasil

        # Cria mapa base
        mapa = self.criar_mapa_base(centro=centro, zoom_inicial=5)

        # Adiciona marcadores
        mapa = self.adicionar_marcadores_emergencia(
            mapa=mapa,
            dados=dados,
            mostrar_popup=True,
            agrupar_marcadores=True
        )

        # Adiciona mapa de calor se houver dados suficientes
        if len(dados) >= 5:
            mapa = self.adicionar_mapa_calor(
                mapa=mapa,
                dados=dados
            )

        # Adiciona minimap para navegação
        plugins.MiniMap().add_to(mapa)

        # Adiciona escala ao mapa usando método nativo do folium
        folium.TileLayer(
            tiles='cartodbpositron',
            name='Base Light',
            control=True,
        ).add_to(mapa)

        # Adiciona fullscreen
        plugins.Fullscreen().add_to(mapa)

        return mapa
