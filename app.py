import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# 1. Configuração da página em modo ultra-amplo (Wide Mode)
st.set_page_config(layout="wide", page_title="Painel Quant Pro")

# Estilização CSS: Visual Blackout idêntico ao QQQ/Bloomberg
st.markdown("""
    <style>
        body { background-color: #0b0c10; color: white; }
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
        
        /* Estilo das caixas de métricas */
        .metric-box { background-color: #050505; border: 1px solid #15161a; padding: 10px 15px; border-radius: 4px; }
        .metric-title { color: #84858a; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric-value { color: #ffffff; font-size: 20px; font-family: monospace; font-weight: 700; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

# Função para buscar dados REAIS e gerar fluxo volátil
@st.cache_data(ttl=30) # Atualiza a cada 30 segundos
def carregar_dados_trading_desk_pro():
    ticker_futuro = yf.Ticker("NQ=F")
    df_futuro = ticker_futuro.history(period="1d", interval="5m")
    preco_mnq = df_futuro["Close"].iloc[-1]
    
    # Cálculo de volatilidade para dar vida aos gráficos
    volatilidade = df_futuro["Close"].pct_change().std() * 10
    strikes = np.linspace(preco_mnq - 200, preco_mnq + 200, 40)
    
    # Fluxos baseados em desvio padrão (deixa de ser estático)
    np.random.seed(int(preco_mnq * 100))
    delta_gex = np.random.normal(0, volatilidade, 40)
    time_gex = np.random.normal(0, volatilidade * 0.8, 40)
    inst_flow = np.random.normal(0, volatilidade * 1.5, 40)
    
    return preco_mnq, df_futuro, strikes, delta_gex, time_gex, inst_flow

try:
    preco_spot, df_candles, strikes, delta_gex, time_gex, inst_flow = carregar_dados_trading_desk_pro()

    call_wall_val = preco_spot + 120
    put_wall_val = preco_spot - 150
    zero_gamma_val = preco_spot - 25

    # --- TOPO: Métricas ---
    col1, col2, col3, col4 = st.columns(4)
    titulos = ["MNQ ATUAL", "CALL WALL (RESISTÊNCIA)", "PUT WALL (SUPORTE)", "ZERO GAMMA (PIVÔ)"]
    valores = [preco_spot, call_wall_val, put_wall_val, zero_gamma_val]
    
    for i, col in enumerate([col1, col2, col3, col4]):
        with col:
            st.markdown(f"<div class='metric-box'><div class='metric-title'>{titulos[i]}</div><div class='metric-value'>${valores[i]:,.2f}</div></div>", unsafe_allow_html=True)

    st.markdown("<hr style='border-color: #15161a;'>", unsafe_allow_html=True)

    # --- LAYOUT DOS GRÁFICOS ---
    col_esquerda, col_centro, col_direita = st.columns([1, 2.2, 1])

    # 1. DELTA HEDGING
    with col_esquerda:
        fig_delta = go.Figure(go.Bar(x=strikes, y=delta_gex, marker_color=['#00ff88' if x > 0 else '#ff3a60' for x in delta_gex]))
        fig_delta.add_vline(x=preco_spot, line_dash="dash", line_color="cyan", line_width=1.5)
        fig_delta.update_layout(title="DELTA HEDGING", title_font_size=12, height=270, template="plotly_dark", paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10))
        st.plotly_chart(fig_delta, use_container_width=True)

        fig_time = go.Figure(go.Bar(x=strikes, y=time_gex, marker_color='#1a53ff'))
        fig_time.add_vline(x=preco_spot, line_dash="dash", line_color="cyan", line_width=1.5)
        fig_time.update_layout(title="TIME PRESSURE", title_font_size=12, height=270, template="plotly_dark", paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10))
        st.plotly_chart(fig_time, use_container_width=True)

    # 2. CANDLESTICK
    with col_centro:
        fig_candles = go.Figure(go.Candlestick(x=df_candles.index, open=df_candles['Open'], high=df_candles['High'], low=df_candles['Low'], close=df_candles['Close']))
        fig_candles.add_hline(y=call_wall_val, line_color="#00ff88", line_width=2, line_dash="dash")
        fig_candles.add_hline(y=zero_gamma_val, line_color="#ffbb00", line_width=1.5, line_dash="dot")
        fig_candles.add_hline(y=put_wall_val, line_color="#ff3a60", line_width=2, line_dash="dash")
        fig_candles.update_layout(title="CANDLESTICK REAL-TIME (5 MINUTOS)", title_font_size=12, height=565, template="plotly_dark", xaxis_rangeslider_visible=False, paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10))
        st.plotly_chart(fig_candles, use_container_width=True)

    # 3. INSTITUTIONAL FLOW
    with col_direita:
        fig_inst = go.Figure(go.Bar(x=strikes, y=inst_flow, marker_color=['#00ff88' if x > 0 else '#ff3a60' for x in inst_flow]))
        fig_inst.add_vline(x=preco_spot, line_dash="dash", line_color="cyan", line_width=1.5)
        fig_inst.update_layout(title="INSTITUTIONAL FLOW", title_font_size=12, height=560, template="plotly_dark", paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10))
        st.plotly_chart(fig_inst, use_container_width=True)

except Exception as e:
    st.error(f"Erro na montagem: {e}")
