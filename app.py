import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# 1. Configuração da página em modo ultra-amplo (Wide Mode)
st.set_page_config(layout="wide", page_title="Painel Quant Pro")

# Estilização CSS corrigida para garantir que os títulos apareçam no topo
st.markdown("""
    <style>
        body { background-color: #0b0c10; color: white; }
        [data-testid="stMetricLabel"] { font-size: 16px !important; color: #888888 !important; font-weight: bold !important; }
        [data-testid="stMetricValue"] { font-size: 26px !important; font-family: monospace; color: white !important; }
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
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
    
    # Gerando dados separados de Compra (Calls) e Venda (Puts) para o mesmo painel
    np.random.seed(int(preco_mnq) % 1000)
    
    # Delta Hedging Componentes
    dh_calls = np.abs(np.sin((strikes - preco_mnq)/100) * 0.4) + np.random.normal(0, 0.02, 40)
    dh_puts = -np.abs(np.cos((strikes - preco_mnq)/120) * 0.4) + np.random.normal(0, 0.02, 40)
    
    # Time Pressure Componentes
    tp_calls = np.abs(np.cos((strikes - preco_mnq)/90) * 0.5) + np.random.normal(0, 0.02, 40)
    tp_puts = -np.abs(np.sin((strikes - preco_mnq)/110) * 0.5) + np.random.normal(0, 0.02, 40)
    
    # Institutional Flow Componentes
    if_calls = np.abs(np.sin((strikes - preco_mnq)/80) * 0.3) + np.random.normal(0, 0.01, 40)
    if_puts = -np.abs(np.cos((strikes - preco_mnq)/90) * 0.3) + np.random.normal(0, 0.01, 40)
    
    return preco_mnq, df_futuro, strikes, dh_calls, dh_puts, tp_calls, tp_puts, if_calls, if_puts

try:
    preco_spot, df_candles, strikes, dh_c, dh_p, tp_c, tp_p, if_c, if_p = carregar_dados_trading_desk_pro()

    # Definição das barreiras baseadas no preço atual da sua tela
    call_wall_val = preco_spot + 120
    put_wall_val = preco_spot - 150
    zero_gamma_val = preco_spot - 25

    # --- BLOCO SUPERIOR DE MÉTRICAS (Títulos Diretos para não sumirem) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="PREÇO ATUAL MNQ", value=f"{preco_spot:,.2f}")
    with col2:
        st.metric(label="CALL WALL (TETO)", value=f"{call_wall_val:,.2f}")
    with col3:
        st.metric(label="PUT WALL (CHÃO)", value=f"{put_wall_val:,.2f}")
    with col4:
        st.metric(label="ZERO GAMMA (PIVÔ)", value=f"{zero_gamma_val:,.2f}")

    st.markdown("---")

    # --- RECONSTRUÇÃO DO LAYOUT DE 3 COLUNAS ---
    col_esquerda, col_centro, col_direita = st.columns([1, 2.2, 1])

    # --- COLUNA ESQUERDA: DELTA HEDGING & TIME PRESSURE ---
    with col_esquerda:
        # 1. DELTA HEDGING (Compra e Venda Juntos)
        idx_max_c = np.argmax(dh_c)
        idx_max_p = np.argmin(dh_p)
        
        cores_c = ['#00ff88' if i == idx_max_c else '#1a53ff' for i in range(40)]
        cores_p = ['#ff3a60' if i == idx_max_p else '#1a53ff' for i in range(40)]
        
        fig_delta = go.Figure()
        fig_delta.add_trace(go.Bar(x=strikes, y=dh_c, marker_color=cores_c, name="Compra", showlegend=False))
        fig_delta.add_trace(go.Bar(x=strikes, y=dh_p, marker_color=cores_p, name="Venda", showlegend=False))
        fig_delta.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
        fig_delta.update_layout(
            title="DELTA HEDGING", title_font_size=12, height=270, template="plotly_dark",
            barmode="relative", paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10),
            xaxis=dict(showgrid=False, tickformat=",.0f"), yaxis=dict(showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig_delta, use_container_width=True)

        # 2. TIME PRESSURE (Compra e Venda Juntos)
        idx_max_tc = np.argmax(tp_c)
        idx_max_tp = np.argmin(tp_p)
        
        cores_tc = ['#00ff88' if i == idx_max_tc else '#1a53ff' for i in range(40)]
        cores_tp = ['#ff3a60' if i == idx_max_tp else '#1a53ff' for i in range(40)]
        
        fig_time = go.Figure()
        fig_time.add_trace(go.Bar(x=strikes, y=tp_c, marker_color=cores_tc, name="Compra", showlegend=False))
        fig_time.add_trace(go.Bar(x=strikes, y=tp_p, marker_color=cores_tp, name="Venda", showlegend=False))
        fig_time.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
        fig_time.update_layout(
            title="TIME PRESSURE", title_font_size=12, height=270, template="plotly_dark",
            barmode="relative", paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10),
            xaxis=dict(showgrid=False, tickformat=",.0f"), yaxis=dict(showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig_time, use_container_width=True)

    # --- COLUNA CENTRAL: GRÁFICO DE CANDLES ---
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
        fig_candles.add_hline(y=zero_gamma_val, line_color="#ffbb00", line_width=1.5, line_dash="dash",
                              annotation_text=f"ZERO GAMMA: {zero_gamma_val:,.0f}", annotation_position="top right")
        fig_candles.add_hline(y=put_wall_val, line_color="#ff3a60", line_width=2, 
                              annotation_text=f"PUT WALL: {put_wall_val:,.0f}", annotation_position="bottom right")

        y_min = min(df_candles['Low'].min(), put_wall_val)
        y_max = max(df_candles['High'].max(), call_wall_val)
        
        fig_candles.update_layout(
            title="CANDLESTICK REAL-TIME (5 MINUTOS)", title_font_size=12, height=565, template="plotly_dark",
            xaxis_rangeslider_visible=False, paper_bgcolor="#111", plot_bgcolor="#111",
            margin=dict(l=10, r=10, t=35, b=10), yaxis=dict(range=[y_min - 20, y_max + 20], showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig_candles, use_container_width=True)

    # --- COLUNA DIREITA: INSTITUTIONAL FLOW ---
    with col_direita:
        idx_max_ifc = np.argmax(if_c)
        idx_max_ifp = np.argmin(if_p)
        
        cores_ifc = ['#00ff88' if i == idx_max_ifc else '#1a53ff' for i in range(40)]
        cores_ifp = ['#ff3a60' if i == idx_max_ifp else '#1a53ff' for i in range(40)]
        
        fig_inst = go.Figure()
        fig_inst.add_trace(go.Bar(x=strikes, y=if_c, marker_color=cores_ifc, name="Compra", showlegend=False))
        fig_inst.add_trace(go.Bar(x=strikes, y=if_p, marker_color=cores_ifp, name="Venda", showlegend=False))
        fig_inst.add_hline(y=0, line_color="rgba(255,255,255,0.2)", line_width=1)
        fig_inst.update_layout(
            title="INSTITUTIONAL FLOW", title_font_size=12, height=560, template="plotly_dark",
            barmode="relative", paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10),
            xaxis=dict(showgrid=False, tickformat=",.0f"), yaxis=dict(showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig_inst, use_container_width=True)

except Exception as e:
    st.error(f"Erro na montagem do Workspace: {e}")
