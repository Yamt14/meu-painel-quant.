import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# 1. Configuração da página em modo ultra-amplo (Wide Mode)
st.set_page_config(layout="wide", page_title="Painel Quant Pro")

# Estilização CSS Avançada: Idêntica ao layout blackout do QQQ / InsiderFinance
st.markdown("""
    <style>
        body { background-color: #0b0c10; color: white; }
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
        
        /* Layout das Caixas do Topo (Estilo QQQ) */
        .metric-row { display: flex; gap: 15px; margin-bottom: 10px; width: 100%; }
        .metric-box { background-color: #050505; padding: 15px 20px; border-radius: 4px; border: 1px solid #15161a; flex: 1; }
        .metric-title { color: #84858a; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }
        .metric-value { color: #ffffff; font-size: 26px; font-family: monospace; font-weight: 700; }
        
        /* Ajuste de espaçamento da linha divisória */
        hr { margin-top: 10px !important; margin-bottom: 15px !important; border-color: #15161a !important; }
    </style>
""", unsafe_allow_html=True)

# Função para buscar os dados reais e montar os 20 strikes do eixo
@st.cache_data(ttl=60)
def carregar_dados_trading_desk_pro():
    try:
        ticker_futuro = yf.Ticker("NQ=F")
        df_futuro = ticker_futuro.history(period="1d", interval="5m")
        if df_futuro.empty:
            df_futuro = ticker_futuro.history(period="5d", interval="5m")
        preco_mnq = df_futuro["Close"].iloc[-1]
    except:
        datas = pd.date_range(end=pd.Timestamp.now(), periods=50, freq='5min')
        df_futuro = pd.DataFrame({
            'Open': np.linspace(19800, 19880, 50),
            'High': np.linspace(19820, 19900, 50),
            'Low': np.linspace(19780, 19860, 50),
            'Close': np.linspace(19810, 19880, 50),
        }, index=datas)
        preco_mnq = 19880.00

    # Criando exatamente 20 degraus para cima e 20 para baixo (total 40 strikes no eixo)
    strikes = np.linspace(preco_mnq - 200, preco_mnq + 200, 40)
    
    # Gerando os fluxos matemáticos estáticos originais para a sessão
    np.random.seed(int(preco_mnq) % 1000)
    delta_hedging = np.sin((strikes - preco_mnq)/80) * 0.4 + np.random.normal(0, 0.04, 40)
    time_pressure = np.cos((strikes - preco_mnq)/100) * 0.5 + np.random.normal(0, 0.04, 40)
    institutional_flow = np.sin((strikes - preco_mnq)/70) * 0.3 + np.random.normal(0, 0.03, 40)
    
    return preco_mnq, df_futuro, strikes, delta_hedging, time_pressure, institutional_flow

try:
    preco_spot, df_candles, strikes, delta_gex, time_gex, inst_flow = carregar_dados_trading_desk_pro()

    # Definição matemática das barreiras baseadas no preço atual
    call_wall_val = preco_spot + 120
    put_wall_val = preco_spot - 150
    zero_gamma_val = preco_spot - 25

    # --- TOPO COMPACTO: Formatação Espelhada Perfeita do Grid do QQQ ---
    st.markdown(f"""
    <div class='metric-row'>
        <div class='metric-box'>
            <div class='metric-title'>Spot Price (MNQ)</div>
            <div class='metric-value'>${preco_spot:,.2f}</div>
        </div>
        <div class='metric-box'>
            <div class='metric-title'>Call Wall</div>
            <div class='metric-value'>${call_wall_val:,.2f}</div>
        </div>
        <div class='metric-box'>
            <div class='metric-title'>Put Wall</div>
            <div class='metric-value'>${put_wall_val:,.2f}</div>
        </div>
        <div class='metric-box'>
            <div class='metric-title'>Zero Gamma</div>
            <div class='metric-value'>${zero_gamma_val:,.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # --- RECONSTRUÇÃO DO LAYOUT DE 3 COLUNAS ---
    col_esquerda, col_centro, col_direita = st.columns([1, 2.2, 1])

    # --- COLUNA ESQUERDA: DELTA HEDGING & TIME PRESSURE ---
    with col_esquerda:
        # 1. DELTA HEDGING (Gráfico Original Restaurado)
        idx_max_pos_delta = np.argmax(delta_gex)
        idx_min_neg_delta = np.argmin(delta_gex)
        
        cores_delta = []
        for i, v in enumerate(delta_gex):
            if i == idx_max_pos_delta:
                cores_delta.append('#00ff88')
            elif i == idx_min_neg_delta:
                cores_delta.append('#ff3a60')
            else:
                cores_delta.append('#1a53ff')
                
        fig_delta = go.Figure()
        fig_delta.add_trace(go.Bar(x=strikes, y=delta_gex, marker_color=cores_delta, showlegend=False))
        fig_delta.add_vline(x=preco_spot, line_dash="dash", line_color="cyan", line_width=1.5)
        fig_delta.update_layout(
            title="DELTA HEDGING", title_font_size=12, height=270, template="plotly_dark",
            paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10),
            xaxis=dict(showgrid=False, tickformat=",.0f"), yaxis=dict(showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig_delta, use_container_width=True)

        # 2. TIME PRESSURE (Gráfico Original Restaurado)
        idx_max_pos_time = np.argmax(time_gex)
        idx_min_neg_time = np.argmin(time_gex)
        
        cores_time = []
        for i, v in enumerate(time_gex):
            if i == idx_max_pos_time:
                cores_time.append('#00ff88')
            elif i == idx_min_neg_time:
                cores_time.append('#ff3a60')
            else:
                cores_time.append('#1a53ff')
                
        fig_time = go.Figure()
        fig_time.add_trace(go.Bar(x=strikes, y=time_gex, marker_color=cores_time, showlegend=False))
        fig_time.add_vline(x=preco_spot, line_dash="dash", line_color="cyan", line_width=1.5)
        fig_time.update_layout(
            title="TIME PRESSURE", title_font_size=12, height=270, template="plotly_dark",
            paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10),
            xaxis=dict(showgrid=False, tickformat=",.0f"), yaxis=dict(showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig_time, use_container_width=True)

    # --- COLUNA CENTRAL: GRÁFICO DE CANDLES ORIGINAL ---
    with col_centro:
        fig_candles = go.Figure()
        fig_candles.add_trace(go.Candlestick(
            x=df_candles.index,
            open=df_candles['Open'], high=df_candles['High'],
            low=df_candles['Low'], close=df_candles['Close'],
            name="MNQ 5m", increasing_line_color='#00ffc2', decreasing_line_color='#ff3a60'
        ))

        fig_candles.add_hline(y=call_wall_val, line_color="#00ff88", line_width=2, 
                              annotation_text=f"CALL WALL: {call_wall_val:,.0f}", annotation_position="top right")
        
        fig_candles.add_hline(y=
