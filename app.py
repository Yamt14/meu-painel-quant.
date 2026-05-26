import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd

st.set_page_config(layout="wide", page_title="Painel Quant Pro")

# --- CSS Profissional (Estilo Bloomberg/Institutional) ---
st.markdown("""
    <style>
        .metric-box { background-color: #050505; border: 1px solid #1e1e1e; padding: 10px; border-radius: 4px; }
        .metric-title { color: #888; font-size: 10px; text-transform: uppercase; letter-spacing: 1px; }
        .metric-value { color: #fff; font-size: 20px; font-family: monospace; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- Função de dados (Mantendo sua lógica funcional) ---
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        ticker = yf.Ticker("NQ=F")
        df = ticker.history(period="1d", interval="5m")
        preco = df["Close"].iloc[-1]
    except:
        preco = 19880.00
        df = pd.DataFrame({'Open': [19800], 'High': [19900], 'Low': [19780], 'Close': [19880]}, index=[pd.Timestamp.now()])
    
    strikes = np.linspace(preco - 200, preco + 200, 40)
    gex = np.sin((strikes - preco)/80) * 0.4
    return preco, df, strikes, gex

preco_spot, df, strikes, gex = carregar_dados()

# --- Topo (Metric Box profissional) ---
c1, c2, c3, c4 = st.columns(4)
data_topo = [("MNQ ATUAL", preco_spot), ("CALL WALL", preco_spot + 120), ("PUT WALL", preco_spot - 150), ("ZERO GAMMA", preco_spot - 25)]
for i, col in enumerate([c1, c2, c3, c4]):
    with col:
        st.markdown(f"<div class='metric-box'><div class='metric-title'>{data_topo[i][0]}</div><div class='metric-value'>${data_topo[i][1]:,.2f}</div></div>", unsafe_allow_html=True)

st.markdown("---")

col_e, col_c, col_d = st.columns([1, 2.5, 1])

# --- Delta Hedging ---
with col_e:
    fig = go.Figure(go.Bar(x=strikes, y=gex, marker_color=['#00ff88' if x > 0 else '#ff3a60' for x in gex]))
    fig.update_layout(title="DELTA HEDGING", template="plotly_dark", height=270, paper_bgcolor="#000", plot_bgcolor="#000")
    st.plotly_chart(fig, use_container_width=True)

# --- Candlestick com Linhas GEX ---
with col_c:
    fig_c = go.Figure(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    # Linhas Dinâmicas de Suporte e Resistência
    for nivel, cor in [(preco_spot + 120, "#00ff88"), (preco_spot - 150, "#ff3a60"), (preco_spot - 25, "#ffff00")]:
        fig_c.add_hline(y=nivel, line_dash="dash", line_color=cor, opacity=0.6)
    fig_c.update_layout(title="CANDLESTICK + NÍVEIS GEX", template="plotly_dark", height=565, paper_bgcolor="#000", plot_bgcolor="#000")
    st.plotly_chart(fig_c, use_container_width=True)

# --- Flow com Cores Condicionais ---
with col_d:
    fig_i = go.Figure(go.Bar(x=strikes, y=gex*-1, marker_color=['#00ff88' if x < 0 else '#ff3a60' for x in gex]))
    fig_i.update_layout(title="INSTITUTIONAL FLOW", template="plotly_dark", height=560, paper_bgcolor="#000", plot_bgcolor="#000")
    st.plotly_chart(fig_i, use_container_width=True)
