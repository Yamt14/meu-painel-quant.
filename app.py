import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd

st.set_page_config(layout="wide", page_title="Painel Quant Pro")

# Função de dados original
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

# Topo: Usando colunas nativas do Streamlit (sem erro de HTML)
c1, c2, c3, c4 = st.columns(4)
c1.metric("MNQ ATUAL", f"${preco_spot:,.2f}")
c2.metric("CALL WALL", f"${preco_spot + 120:,.2f}")
c3.metric("PUT WALL", f"${preco_spot - 150:,.2f}")
c4.metric("ZERO GAMMA", f"${preco_spot - 25:,.2f}")

st.markdown("---")

# Gráficos Originais
col_e, col_c, col_d = st.columns([1, 2.2, 1])

with col_e:
    fig = go.Figure(go.Bar(x=strikes, y=gex, marker_color='#1a53ff'))
    fig.update_layout(title="DELTA HEDGING", template="plotly_dark", height=270)
    st.plotly_chart(fig, use_container_width=True)

with col_c:
    fig_c = go.Figure(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    fig_c.update_layout(title="CANDLESTICK", template="plotly_dark", height=565)
    st.plotly_chart(fig_c, use_container_width=True)

with col_d:
    fig_i = go.Figure(go.Bar(x=strikes, y=gex*-1, marker_color='#1a53ff'))
    fig_i.update_layout(title="FLOW", template="plotly_dark", height=560)
    st.plotly_chart(fig_i, use_container_width=True)
    
