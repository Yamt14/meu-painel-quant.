import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 1. Configuração da página estilo Trading Desk
st.set_page_config(layout="wide", page_title="Painel Quantico Clone")
st.title("📊 Painel Quant – Automação de Suportes e Resistências Dinâmicas")

# Função para buscar e calcular os dados (com cache para ficar rápido)
@st.cache_data(ttl=300)  # Atualiza a cada 5 minutos
def carregar_dados_mercado():
    ticker = yf.Ticker("QQQ")
    
    # Preço atual do ETF
    preco_atual = ticker.history(period="1d")["Close"].iloc[-1]
    
    # Pegar a data de expiração mais próxima com bastante liquidez
    expiracoes = ticker.options
    data_alvo = expiracoes[2] # Geralmente a terceira expiração da lista tem ótimo volume institucional
    
    grade_opcoes = ticker.option_chain(data_alvo)
    calls = grade_opcoes.calls
    puts = grade_opcoes.puts
    
    # Lógica Quant: Encontrar onde as instituições montaram as maiores barreiras (Walls)
    call_wall_strike = calls.loc[calls['openInterest'].idxmax()]['strike']
    put_wall_strike = puts.loc[puts['openInterest'].idxmax()]['strike']
    
    # Zero Gamma Aproximado (ponto médio de transição de liquidez perto do preço atual)
    zero_gamma_aprox = (call_wall_strike + put_wall_strike) / 2
    
    return preco_atual, call_wall_strike, put_wall_strike, zero_gamma_aprox, data_alvo, calls, puts

# Executar a busca de dados
try:
    preco_spot, call_wall, put_wall, zero_gamma, vencimento, df_calls, df_puts = carregar_dados_mercado()
    
    # --- BLOCOS SUPERIORES DE MÉTRICAS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="QQQ Preço Spot (Real)", value=f"${preco_spot:.2f}")
    with col2:
        st.metric(label="CALL WALL (Resistência Máxima)", value=f"${call_wall:.2f}")
    with col3:
        st.metric(label="PUT WALL (Suporte Máximo)", value=f"${put_wall:.2f}")
    with col4:
        st.metric(label="Gatilho de Volatilidade", value=f"${zero_gamma:.2f}")

    st.caption(f"Análise baseada no vencimento de opções de: **{vencimento}**")
    st.markdown("---")

    # --- CORPO PRINCIPAL (Gráfico Central + Fluxo de Liquidez) ---
    col_grafico, col_lateral = st.columns([3, 1])

    with col_grafico:
        st.subheader("Gráfico de Linhas Dinâmicas de Opções")
        
        fig = go.Figure()
        
        # Plotar as linhas calculadas automaticamente pelo algoritmo
        fig.add_hline(y=preco_spot, line_dash="dot", line_color="blue", line_width=2, annotation_text="Preço Spot Atual")
        fig.add_hline(y=call_wall, line_color="green", line_width=4, annotation_text="CALL WALL (Muralha Vendedora)")
        fig.add_hline(y=zero_gamma, line_dash="dash", line_color="yellow", line_width=2, annotation_text="Eixo de Pivô Quant")
        fig.add_hline(y=put_wall, line_color="red", line_width=4, annotation_text="PUT WALL (Muralha Compradora)")
        
        # Ajustar o visual para modo escuro profissional
        fig.update_layout(
            height=500, 
            template="plotly_dark", 
            yaxis_range=[put_wall - 15, call_wall + 15],
            paper_bgcolor="#111", 
            plot_bgcolor="#111"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_lateral:
        st.subheader("Estratégia Quantico")
        
        # Tomada de decisão automatizada baseada no preço vs barreiras
        if preco_spot > zero_gamma:
            st.success("🟢 **REGIME:** Bullish/Positive Gamma. O mercado tende a segurar quedas e buscar a Call Wall.")
        else:
            st.error("🔴 **REGIME:** Bearish/Negative Gamma. Volatilidade pode acelerar em direção à Put Wall.")
            
        st.info(f"🎯 **Alvo de Atração:** O preço tende a ser atraído para os **${call_wall:.2f}** se houver volume comprador.")

except Exception as e:
    st.error(f"Erro ao conectar com a API de dados: {e}")
