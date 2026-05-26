import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd

# 1. Configuração da página para ocupar a tela inteira (Wide Mode)
st.set_page_config(layout="wide", page_title="Painel Quant Pro")

# Estilização CSS para deixar os blocos escuros e colados estilo Dashboard profissional
st.markdown("""
    <style>
        body { background-color: #0b0c10; color: #white; }
        [data-testid="stMetricValue"] { font-size: 24px !important; font-family: monospace; }
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
    </style>
""", unsafe_allow_html=True)

# Função para buscar dados reais e estruturar o fluxo quantitativo simulado
@st.cache_data(ttl=60)
def carregar_dados_trading_desk():
    try:
        ticker_futuro = yf.Ticker("NQ=F")
        df_futuro = ticker_futuro.history(period="1d", interval="5m")
        if df_futuro.empty:
            df_futuro = ticker_futuro.history(period="5d", interval="5m")
        preco_mnq = df_futuro["Close"].iloc[-1]
    except:
        # Backup estável se a API falhar ou mercado estiver fechado
        datas = pd.date_range(end=pd.Timestamp.now(), periods=50, freq='5min')
        df_futuro = pd.DataFrame({
            'Open': np.linspace(19800, 19880, 50),
            'High': np.linspace(19820, 19900, 50),
            'Low': np.linspace(19780, 19860, 50),
            'Close': np.linspace(19810, 19880, 50),
        }, index=datas)
        preco_mnq = 19880.00

    # Criação dos eixos de strikes para os gráficos laterais (GEX Profile)
    strikes = np.linspace(preco_mnq - 150, preco_mnq + 150, 15)
    
    # Geração dos fluxos institucionais simulados baseados no preço atual
    np.random.seed(int(preco_mnq) % 1000)
    delta_hedging = np.sin((strikes - preco_mnq)/60) * 0.4 + np.random.normal(0, 0.05, 15)
    time_pressure = np.cos((strikes - preco_mnq)/80) * 0.5 + np.random.normal(0, 0.05, 15)
    institutional_flow = np.sin((strikes - preco_mnq)/50) * 0.2 + np.random.normal(0, 0.03, 15)
    
    return preco_mnq, df_futuro, strikes, delta_hedging, time_pressure, institutional_flow

try:
    preco_spot, df_candles, strikes, delta_gex, time_gex, inst_flow = carregar_dados_trading_desk()

    # --- LINHA SUPERIOR: PREÇO E RELÓGIO ---
    col_tit, col_clock = st.columns([3, 1])
    with col_tit:
        st.subheader(f"📊 INSTITUTIONAL DESK — MNQ NASDAQ FUTUROS: {preco_spot:,.2f}")
    with col_clock:
        st.markdown(f"<p style='text-align:right; font-family:monospace; color:#888;'>SESSÃO LIVE NY</p>", unsafe_allow_html=True)

    # --- DIVISÃO DA TELA EM COLUNAS OPERACIONAIS (Estilo Quântico Cap) ---
    # Colona 1 (Esquerda: Delta Hedging e Time Pressure) | Coluna 2 (Centro: Candles) | Coluna 3 (Direita: Institutional Flow)
    col_esquerda, col_centro, col_direita = st.columns([1, 2.2, 1])

    # --- COLUNA ESQUERDA (DELTA HEDGING & TIME PRESSURE) ---
    with col_esquerda:
        # 1. Gráfico DELTA HEDGING
        fig_delta = go.Figure()
        cores_delta = ['#00ffc2' if v >= 0 else '#ff3a60' for v in delta_gex]
        fig_delta.add_trace(go.Bar(x=strikes, y=delta_gex, marker_color=cores_delta, showlegend=False))
        fig_delta.add_vline(x=preco_spot, line_dash="dash", line_color="cyan", line_width=1)
        fig_delta.update_layout(
            title="DELTA HEDGING", title_font_size=12, height=270, template="plotly_dark",
            paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10),
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig_delta, use_container_width=True)

        # 2. Gráfico TIME PRESSURE
        fig_time = go.Figure()
        cores_time = ['#00ffc2' if v >= 0 else '#ff3a60' for v in time_gex]
        fig_time.add_trace(go.Bar(x=strikes, y=time_gex, marker_color=cores_time, showlegend=False))
        fig_time.add_vline(x=preco_spot, line_dash="dash", line_color="cyan", line_width=1)
        fig_time.update_layout(
            title="TIME PRESSURE", title_font_size=12, height=270, template="plotly_dark",
            paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10),
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig_time, use_container_width=True)

    # --- COLUNA CENTRAL (CANDLESTICK CHART ORIGINAL) ---
    with col_centro:
        fig_candles = go.Figure()
        fig_candles.add_trace(go.Candlestick(
            x=df_candles.index,
            open=df_candles['Open'], high=df_candles['High'],
            low=df_candles['Low'], close=df_candles['Close'],
            name="MNQ 5m", increasing_line_color='#00ffc2', decreasing_line_color='#ff3a60'
        ))
        # Ajuste de escala dinâmico para os candles ficarem grandes e nítidos
        y_min, y_max = df_candles['Low'].min(), df_candles['High'].max()
        fig_candles.update_layout(
            title="CANDLESTICK / LINE CHART (5 MINUTOS)", title_font_size=12, height=565, template="plotly_dark",
            xaxis_rangeslider_visible=False, paper_bgcolor="#111", plot_bgcolor="#111",
            margin=dict(l=10, r=10, t=35, b=10), yaxis=dict(range=[y_min - 10, y_max + 10], showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig_candles, use_container_width=True)

    # --- COLUNA DIREITA (INSTITUTIONAL FLOW) ---
    with col_direita:
        fig_inst = go.Figure()
        cores_inst = ['#00ffc2' if v >= 0 else '#ff3a60' for v in inst_flow]
        fig_inst.add_trace(go.Bar(x=strikes, y=inst_flow, marker_color=cores_inst, showlegend=False))
        fig_inst.add_vline(x=preco_spot, line_dash="dash", line_color="cyan", line_width=1)
        fig_inst.update_layout(
            title="INSTITUTIONAL FLOW", title_font_size=12, height=560, template="plotly_dark",
            paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10),
            xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig_inst, use_container_width=True)

except Exception as e:
    st.error(f"Erro na montagem da Mesa de Operações: {e}")
