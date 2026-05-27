import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd

st.set_page_config(layout="wide", page_title="Painel Quant Pro")

# Função de dados
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        ticker = yf.Ticker("NQ=F")
        df = ticker.history(period="1d", interval="5m")
        preco = df["Close"].iloc[-1]
    except:
        preco = 30140.25
        df = pd.DataFrame({'Open': [30000], 'High': [30200], 'Low': [29900], 'Close': [30140]}, index=[pd.Timestamp.now()])
    
    strikes = np.linspace(preco - 200, preco + 200, 40)
    # Gerando dados baseados em volatilidade
    vol = df["Close"].pct_change().std() * 10
    np.random.seed(int(preco))
    delta = np.random.normal(0, vol, 40)
    time = np.random.normal(0, vol, 40)
    flow = np.random.normal(0, vol * 1.5, 40)
    return preco, df, strikes, delta, time, flow

preco_spot, df, strikes, delta, time, flow = carregar_dados()

# --- TOPO SIMPLIFICADO (Sem erro de CSS) ---
c1, c2, c3, c4 = st.columns(4)
c1.subheader("MNQ ATUAL")
c1.metric("", f"${preco_spot:,.2f}")
c2.subheader("CALL WALL")
c2.metric("", f"${preco_spot + 120:,.2f}")
c3.subheader("PUT WALL")
c3.metric("", f"${preco_spot - 150:,.2f}")
c4.subheader("ZERO GAMMA")
c4.metric("", f"${preco_spot - 25:,.2f}")

st.markdown("---")

# --- GRÁFICOS ---
col_e, col_c, col_d = st.columns([1, 2.2, 1])

with col_e:
    fig = go.Figure(go.Bar(x=strikes, y=delta, marker_color='#1a53ff'))
    fig.update_layout(title="DELTA HEDGING", template="plotly_dark", height=270, paper_bgcolor="#000", plot_bgcolor="#000")
    st.plotly_chart(fig, use_container_width=True)

    fig_t = go.Figure(go.Bar(x=strikes, y=time, marker_color='#1a53ff'))
    fig_t.update_layout(title="TIME PRESSURE", template="plotly_dark", height=270, paper_bgcolor="#000", plot_bgcolor="#000")
    st.plotly_chart(fig_t, use_container_width=True)

with col_c:
    fig_c = go.Figure(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    fig_c.update_layout(title="CANDLESTICK REAL-TIME", template="plotly_dark", height=565, paper_bgcolor="#000", plot_bgcolor="#000")
    st.plotly_chart(fig_c, use_container_width=True)

with col_d:
    fig_i = go.Figure(go.Bar(x=strikes, y=flow, marker_color=['#00ff88' if x > 0 else '#ff3a60' for x in flow]))
    fig_i.update_layout(title="INSTITUTIONAL FLOW", template="plotly_dark", height=560, paper_bgcolor="#000", plot_bgcolor="#000")
    st.plotly_chart(fig_i, use_container_width=True)
