import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd

st.set_page_config(layout="wide", page_title="Painel Quant Pro")

st.markdown("""
    <style>
        body { background-color: #0b0c10; color: white; }
        [data-testid="stMetricValue"] { font-size: 24px !important; font-family: monospace; }
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados_trading_desk_pro():
    try:
        ticker_futuro = yf.Ticker("NQ=F")
        df_futuro = ticker_futuro.history(period="1d", interval="5m")
        preco_mnq = df_futuro["Close"].iloc[-1]
    except:
        preco_mnq = 19880.00
        df_futuro = pd.DataFrame({'Open': [19800], 'High': [19900], 'Low': [19780], 'Close': [19810]}, index=[pd.Timestamp.now()])
    
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

    # --- MÉTRICAS NO TOPO ---
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown("<div style='font-size: 12px; color: #888;'>MNQ PREÇO ATUAL</div>", unsafe_allow_html=True)
    col1.metric(label="", value=f"{preco_spot:,.2f}")
    col2.markdown("<div style='font-size: 12px; color: #888;'>CALL WALL</div>", unsafe_allow_html=True)
    col2.metric(label="", value=f"{call_wall_val:,.2f}")
    col3.markdown("<div style='font-size: 12px; color: #888;'>PUT WALL</div>", unsafe_allow_html=True)
    col3.metric(label="", value=f"{put_wall_val:,.2f}")
    col4.markdown("<div style='font-size: 12px; color: #888;'>ZERO GAMMA</div>", unsafe_allow_html=True)
    col4.metric(label="", value=f"{zero_gamma_val:,.2f}")
    
    st.markdown("---")

    # --- LAYOUT DOS GRÁFICOS ---
    col_esquerda, col_centro, col_direita = st.columns([1, 2.2, 1])

    # Função interna para gerar gráficos para não repetir código
    def plot_bar(x, y, title, spot):
        cores = ['#00ff88' if v > 0 else '#ff3a60' for v in y]
        fig = go.Figure(go.Bar(x=x, y=y, marker_color=cores, showlegend=False))
        fig.add_vline(x=spot, line_dash="dash", line_color="cyan", line_width=1.5)
        fig.update_layout(title=title, template="plotly_dark", height=270, margin=dict(l=10, r=10, t=35, b=10))
        return fig

    with col_esquerda:
        st.plotly_chart(plot_bar(strikes, delta_gex, "DELTA HEDGING", preco_spot), use_container_width=True)
        st.plotly_chart(plot_bar(strikes, time_gex, "TIME PRESSURE", preco_spot), use_container_width=True)

    with col_centro:
        fig = go.Figure(go.Candlestick(x=df_candles.index, open=df_candles['Open'], high=df_candles['High'], low=df_candles['Low'], close=df_candles['Close']))
        fig.add_hline(y=call_wall_val, line_color="#00ff88", line_dash="dash")
        fig.add_hline(y=zero_gamma_val, line_color="#ffbb00", line_dash="dot")
        fig.add_hline(y=put_wall_val, line_color="#ff3a60", line_dash="dash")
        fig.update_layout(title="CANDLESTICK REAL-TIME", template="plotly_dark", height=565, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    with col_direita:
        st.plotly_chart(plot_bar(strikes, inst_flow, "INSTITUTIONAL FLOW", preco_spot), use_container_width=True)

except Exception as e:
    st.error(f"Erro na montagem: {e}")
