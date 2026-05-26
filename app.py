import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd

st.set_page_config(layout="wide", page_title="Painel Quant Pro")

# Estilização CSS: Visual Blackout estilo QQQ
st.markdown("""
    <style>
        body { background-color: #0b0c10; color: white; }
        .block-container { padding-top: 1rem; }
        
        /* Estilo das colunas (Simulando as caixas do QQQ) */
        .box {
            background-color: #050505;
            border: 1px solid #15161a;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
        }
        .title { color: #84858a; font-size: 11px; font-weight: 700; text-transform: uppercase; margin-bottom: 5px; }
        .value { color: #ffffff; font-size: 22px; font-family: monospace; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# Função de dados
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

# Topo: Layout de colunas com HTML customizado
c1, c2, c3, c4 = st.columns(4)
colunas = [c1, c2, c3, c4]
titulos = ["MNQ ATUAL", "CALL WALL", "PUT WALL", "ZERO GAMMA"]
valores = [preco_spot, preco_spot + 120, preco_spot - 150, preco_spot - 25]

for i, col in enumerate(colunas):
    with col:
        st.markdown(f"""
            <div class='box'>
                <div class='title'>{titulos[i]}</div>
                <div class='value'>${valores[i]:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("<hr style='border-color: #15161a;'>", unsafe_allow_html=True)

# Gráficos (Mantendo sua lógica original)
col_e, col_c, col_d = st.columns([1, 2.2, 1])

with col_e:
    fig = go.Figure(go.Bar(x=strikes, y=gex, marker_color='#1a53ff'))
    fig.update_layout(title="DELTA HEDGING", template="plotly_dark", height=270, paper_bgcolor="#111", plot_bgcolor="#111")
    st.plotly_chart(fig, use_container_width=True)

with col_c:
    fig_c = go.Figure(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close']))
    fig_c.update_layout(title="CANDLESTICK", template="plotly_dark", height=565, paper_bgcolor="#111", plot_bgcolor="#111")
    st.plotly_chart(fig_c, use_container_width=True)

with col_d:
    fig_i = go.Figure(go.Bar(x=strikes, y=gex*-1, marker_color='#1a53ff'))
    fig_i.update_layout(title="FLOW", template="plotly_dark", height=560, paper_bgcolor="#111", plot_bgcolor="#111")
    st.plotly_chart(fig_i, use_container_width=True)
