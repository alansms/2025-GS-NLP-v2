"""
Script para adicionar a funcionalidade de análise de sentimento no app.py
Este script mostra as alterações necessárias que devem ser feitas no arquivo app.py
"""

# Modificação 1: Na linha 623, alterar a definição das abas para incluir "Análise de Sentimento"
# De: tab1, tab2, tab3, tab4, tab5 = st.tabs(["Mensagens", "Gráficos", "Mapa", "Nuvem de Palavras", "Análise de Texto"])
# Para: tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Mensagens", "Gráficos", "Mapa", "Nuvem de Palavras", "Análise de Texto", "Análise de Sentimento"])

# Modificação 2: Adicionar o código para a nova aba de análise de sentimento após a aba "Análise de Texto"
# Este código deve ser inserido após o fechamento do bloco "with tab5:" (por volta da linha 850)

"""
        with tab6:
            # Análise de Sentimento
            st.subheader("🧠 Análise de Sentimento")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.write("**Análise de Sentimento de Novas Mensagens**")
                
                # Campo para o usuário inserir um texto para análise
                texto_para_analise = st.text_area(
                    "Digite uma mensagem para análise de sentimento:",
                    height=150,
                    placeholder="Ex: Urgente! Precisamos de ajuda imediata. Inundação na Rua das Flores, nº 123. Família com crianças ilhada no telhado."
                )
                
                # Seleção do método de análise
                metodo_analise = st.radio(
                    "Selecione o método de análise:",
                    ["VADER", "TextBlob"],
                    horizontal=True
                )
                
                if st.button("Analisar Sentimento"):
                    if texto_para_analise:
                        try:
                            # Instanciar o analisador de sentimento com o método selecionado
                            analisador = AnalisadorSentimento(metodo=metodo_analise.lower())
                            
                            # Realizar a análise de sentimento
                            resultado = analisador.analisar_mensagem(texto_para_analise)
                            
                            # Exibir resultados em um card com estilos
                            sentimento = resultado['sentimento']
                            score = resultado['score_composto']
                            nivel_urgencia = resultado['nivel_urgencia']
                            score_urgencia = resultado['score_urgencia']
                            
                            st.markdown(f"""
                            <div style="border-left: 5px solid #1E88E5; padding: 15px; background-color: #E3F2FD; border-radius: 5px; margin-bottom: 20px;">
                                <h4>Resultado da Análise</h4>
                                <p><strong>Sentimento:</strong> {sentimento}</p>
                                <p><strong>Score de Sentimento:</strong> {score:.4f}</p>
                                <p><strong>Nível de Urgência:</strong> {nivel_urgencia}</p>
                                <p><strong>Score de Urgência:</strong> {score_urgencia:.1f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Palavras-chave identificadas
                            palavras_urgencia = resultado['palavras_urgencia']
                            if palavras_urgencia:
                                st.write("**Palavras-chave de urgência identificadas:**")
                                st.write(", ".join(palavras_urgencia))
                            
                        except Exception as e:
                            st.error(f"Erro na análise de sentimento: {str(e)}")
                    else:
                        st.warning("Por favor, digite uma mensagem para análise.")
            
            with col2:
                st.write("**Estatísticas de Sentimento do Conjunto de Dados**")
                
                try:
                    # Verificar se as colunas necessárias existem
                    if 'sentimento' in df_filtrado.columns and 'score_composto' in df_filtrado.columns:
                        # Distribuição de sentimentos
                        sentimentos_count = df_filtrado['sentimento'].value_counts().reset_index()
                        sentimentos_count.columns = ['Sentimento', 'Contagem']
                        
                        # Gráfico de distribuição de sentimentos
                        fig_sentimentos = px.pie(
                            sentimentos_count, 
                            values='Contagem', 
                            names='Sentimento',
                            title='Distribuição de Sentimentos',
                            color_discrete_sequence=px.colors.qualitative.Set3,
                            hole=0.4
                        )
                        st.plotly_chart(fig_sentimentos, use_container_width=True)
                        
                        # Correlação entre sentimento e urgência
                        st.write("**Relação entre Sentimento e Urgência**")
                        
                        # Gráfico de dispersão
                        if 'score_urgencia' in df_filtrado.columns:
                            fig_scatter = px.scatter(
                                df_filtrado,
                                x='score_composto',
                                y='score_urgencia',
                                color='nivel_urgencia',
                                hover_data=['texto'],
                                title='Correlação entre Sentimento e Urgência',
                                labels={
                                    'score_composto': 'Score de Sentimento',
                                    'score_urgencia': 'Score de Urgência',
                                    'nivel_urgencia': 'Nível de Urgência'
                                }
                            )
                            st.plotly_chart(fig_scatter, use_container_width=True)
                        
                        # Estatísticas de sentimento por tipo de desastre
                        if 'tipo_desastre' in df_filtrado.columns:
                            st.write("**Sentimento Médio por Tipo de Desastre**")
                            
                            # Calcular a média de sentimento por tipo de desastre
                            sentimento_por_tipo = df_filtrado.groupby('tipo_desastre')['score_composto'].mean().reset_index()
                            sentimento_por_tipo.columns = ['Tipo de Desastre', 'Score Médio de Sentimento']
                            
                            # Ordenar do mais negativo para o mais positivo
                            sentimento_por_tipo = sentimento_por_tipo.sort_values('Score Médio de Sentimento')
                            
                            # Gráfico de barras
                            fig_bar = px.bar(
                                sentimento_por_tipo,
                                x='Tipo de Desastre',
                                y='Score Médio de Sentimento',
                                title='Score Médio de Sentimento por Tipo de Desastre',
                                color='Score Médio de Sentimento',
                                color_continuous_scale='RdYlGn'  # Vermelho para negativo, verde para positivo
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)
                    else:
                        st.warning("Dados de sentimento não disponíveis no conjunto de dados atual.")
                        
                        # Oferecer opção para processar os dados
                        if st.button("Processar Sentimentos"):
                            try:
                                with st.spinner("Processando análise de sentimento para todo o conjunto de dados..."):
                                    # Inicializar o analisador
                                    analisador = AnalisadorSentimento()
                                    
                                    # Criar uma cópia do DataFrame
                                    df_com_sentimento = df_filtrado.copy()
                                    
                                    # Aplicar análise de sentimento a cada mensagem
                                    resultados = []
                                    for texto in df_com_sentimento['texto']:
                                        if isinstance(texto, str):
                                            resultado = analisador.analisar_mensagem(texto)
                                            resultados.append(resultado)
                                        else:
                                            resultados.append({
                                                'sentimento': 'neutro', 
                                                'score_composto': 0.0,
                                                'nivel_urgencia': 'baixa',
                                                'score_urgencia': 0
                                            })
                                    
                                    # Adicionar resultados ao DataFrame
                                    df_com_sentimento['sentimento'] = [r['sentimento'] for r in resultados]
                                    df_com_sentimento['score_composto'] = [r['score_composto'] for r in resultados]
                                    df_com_sentimento['nivel_urgencia'] = [r['nivel_urgencia'] for r in resultados]
                                    df_com_sentimento['score_urgencia'] = [r['score_urgencia'] for r in resultados]
                                    
                                    # Atualizar o DataFrame na sessão
                                    st.session_state.dados_processados = df_com_sentimento
                                    
                                    st.success("Análise de sentimento concluída! Atualize a página para ver os resultados.")
                                    st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Erro ao processar sentimentos: {str(e)}")
                
                except Exception as e:
                    st.error(f"Erro ao gerar estatísticas de sentimento: {str(e)}")
"""
