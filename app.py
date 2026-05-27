import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide", page_title="Painel Quant Pro")
st.title("Painel Quant Pro")

# --- Dados (Mantendo sua lógica de strikes) ---
base_time = datetime.now()
prices = np.linspace(29800, 30200, 24)
candles_df = pd.DataFrame({
    'Open': prices - np.random.uniform(5, 15, 24),
    'High': prices + np.random.uniform(10, 25, 24),
    'Low': prices - np.random.uniform(10, 25, 24),
    'Close': prices,
}, index=pd.date_range(end=base_time, periods=24, freq='5min'))

strikes = np.arange(29800, 30500, 50)
delta = np.random.normal(0, 0.003, len(strikes))
time_p = np.random.normal(0, 0.005, len(strikes))
flow = np.random.normal(0, 0.008, len(strikes))

# --- Função de gráfico de barras com cores condicionais (Verde/Vermelho) ---
def create_bar_chart(x, y, title):
    colors = ['#26a69a' if val >= 0 else '#ef5350' for val in y]
    # Destaque ciano para o maior absoluto
    max_idx = np.argmax(np.abs(y))
    colors[max_idx] = '#00ffff'
    
    fig = go.Figure(go.Bar(x=x, y=y, marker_color=colors))
    fig.update_layout(title=title, template="plotly_dark", margin=dict(l=10, r=10, t=35, b=10))
    fig.add_vline(x=30144, line_dash="dash", line_color="#00ffff")
    return fig

# --- Bloco do Topo ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("MNQ ATUAL", "$30,144.25")
c2.metric("CALL WALL", "$30,264.25")
c3.metric("PUT WALL", "$29,994.25")
c4.metric("ZERO GAMMA", "$30,119.25")
st.markdown("---")

# --- Layout dos Gráficos ---
col_e, col_c, col_d = st.columns([1, 2, 1])

with col_e:
    st.plotly_chart(create_bar_chart(strikes, delta, "DELTA HEDGING"), use_container_width=True)
    st.plotly_chart(create_bar_chart(strikes, time_p, "TIME PRESSURE"), use_container_width=True)

with col_c:
    # CANDLESTICK CORRETO
    fig_candles = go.Figure(data=[go.Candlestick(
        x=candles_df.index,
        open=candles_df['Open'], high=candles_df['High'],
        low=candles_df['Low'], close=candles_df['Close'],
        increasing_line_color='#26a69a', decreasing_line_color='#ef5350'
    )])
    fig_candles.update_layout(title="CANDLESTICK REAL-TIME", template="plotly_dark", 
                              xaxis_rangeslider_visible=False, margin=dict(l=10, r=10, t=35, b=10))
    st.plotly_chart(fig_candles, use_container_width=True)

with col_d:
    st.plotly_chart(create_bar_chart(strikes, flow, "INSTITUTIONAL FLOW"), use_container_width=True)
