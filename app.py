import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# 1. Configuração da página em modo ultra-amplo (Wide Mode)
st.set_page_config(layout="wide", page_title="Painel Quant Pro")

# Estilização CSS original (fundo preto e métricas)
st.markdown("""
    <style>
        body { background-color: #0b0c10; color: white; }
        [data-testid="stMetricValue"] { font-size: 24px !important; font-family: monospace; }
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    </style>
""", unsafe_allow_html=True)

# Função de dados (Mantendo a que você já validou)
@st.cache_data(ttl=60)
def carregar_dados_trading_desk_pro():
    try:
        ticker_futuro = yf.Ticker("NQ=F")
        df_futuro = ticker_futuro.history(period="1d", interval="5m")
        preco_mnq = df_futuro["Close"].iloc[-1]
    except:
        preco_mnq = 30100.00
        df_futuro = pd.DataFrame({'Open': [30000], 'High': [30200], 'Low': [29900], 'Close': [30100]}, index=[pd.Timestamp.now()])
    
    strikes = np.linspace(preco_mnq - 200, preco_mnq + 200, 40)
    np.random.seed(int(preco_mnq) % 1000)
    delta_hedging = np.sin((strikes - preco_mnq)/80) * 0.4 + np.random.normal(0, 0.04, 40)
    time_pressure = np.cos((strikes - preco_mnq)/100) * 0.5 + np.random.normal(0, 0.04, 40)
    institutional_flow = np.sin((strikes - preco_mnq)/70) * 0.3 + np.random.normal(0, 0.03, 40)
    return preco_mnq, df_futuro, strikes, delta_hedging, time_pressure, institutional_flow

try:
    preco_spot, df_candles, strikes, delta_gex, time_gex, inst_flow = carregar_dados_trading_desk_pro()

    call_wall_val = preco_spot + 120
    put_wall_val = preco_spot - 150
    zero_gamma_val = preco_spot - 25

    # --- TOPO: Mapeamento direto (O segredo para os títulos aparecerem é usar o label do st.metric) ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("MNQ ATUAL", f"{preco_spot:,.2f}")
    col2.metric("CALL WALL (RESISTÊNCIA)", f"{call_wall_val:,.2f}")
    col3.metric("PUT WALL (SUPORTE)", f"{put_wall_val:,.2f}")
    col4.metric("ZERO GAMMA (PIVÔ)", f"{zero_gamma_val:,.2f}")

    st.markdown("---")

    # --- RESTANTE DO LAYOUT ---
    col_esquerda, col_centro, col_direita = st.columns([1, 2.2, 1])

    # [O restante do código de gráficos permanece exatamente igual ao seu original]
    # ... (cole aqui seu código de gráficos para garantir que nada mude)
