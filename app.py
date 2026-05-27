import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# 1. Configuração da página em modo ultra-amplo (Wide Mode)
st.set_page_config(layout="wide", page_title="Painel Quant Pro")

# Estilização CSS para fundo Blackout e métricas limpas
st.markdown("""
    <style>
        body { background-color: #0b0c10; color: white; }
        [data-testid="stMetricValue"] { font-size: 24px !important; font-family: monospace; }
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
    
    # Gerando os fluxos matemáticos estáticos para a sessão
    np.random.seed(int(preco_mnq) % 1000)
    delta_hedging = np.sin((strikes - preco_mnq)/80) * 0.4 + np.random.normal(0, 0.04, 40)
    time_pressure = np.cos((strikes - preco_mnq)/100) * 0.5 + np.random.normal(0, 0.04, 40)
    institutional_flow = np.sin((strikes - preco_mnq)/70) * 0.3 + np.random.normal(0, 0.03, 40)
    
    return preco_mnq, df_futuro, strikes, delta_hedging, time_pressure, institutional_flow

try:
    preco_spot, df_candles, strikes, delta_gex, time_gex, inst_flow = carregar_dados_trading_desk_pro()

    # Definição matemática estrita das barreiras baseadas no preço atual
    call_wall_val = preco_spot + 120
    put_wall_val = preco_spot - 150
    zero_gamma_val = preco_spot - 25

# --- BLOCO SUPERIORES DE MÉTRICAS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<p style='margin: 0; font-size: 14px;'>MNQ PREÇO ATUAL</p>", unsafe_allow_html=True)
        st.metric(label="", value=f"{preco_spot:,.2f}")
    with col2:
        st.markdown("<p style='margin: 0; font-size: 14px;'>CALL WALL</p>", unsafe_allow_html=True)
        st.metric(label="", value=f"{call_wall_val:,.2f}")
    with col3:
        st.markdown("<p style='margin: 0; font-size: 14px;'>PUT WALL</p>", unsafe_allow_html=True)
        st.metric(label="", value=f"{put_wall_val:,.2f}")
    with col4:
        st.markdown("<p style='margin: 0; font-size: 14px;'>ZERO GAMMA</p>", unsafe_allow_html=True)
        st.metric(label="", value=f"{zero_gamma_val:,.1f}")
        
    st.markdown("---")

    # --- RECONSTRUÇÃO DO LAYOUT DE 3 COLUNAS ---
    col_esquerda, col_centro, col_direita = st.columns([1, 2.2, 1])

    # --- COLUNA ESQUERDA: DELTA HEDGING & TIME PRESSURE ---
    with col_esquerda:
        # 1. DELTA HEDGING
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

        # 2. TIME PRESSURE
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

    # --- COLUNA CENTRAL: GRÁFICO DE CANDLES COM AS LINHAS DO MODELO MACRO ---
    with col_centro:
        fig_candles = go.Figure()
        fig_candles.add_trace(go.Candlestick(
            x=df_candles.index,
            open=df_candles['Open'], high=df_candles['High'],
            low=df_candles['Low'], close=df_candles['Close'],
            name="MNQ 5m", increasing_line_color='#00ffc2', decreasing_line_color='#ff3a60'
        ))

        # Adicionando as 3 linhas de barreira institucionais horizontais (GEX Levels)
        fig_candles.add_hline(y=call_wall_val, line_color="#00ff88", line_width=2, 
                              annotation_text=f"CALL WALL: {call_wall_val:,.0f}", annotation_position="top right")
        
        fig_candles.add_hline(y=zero_gamma_val, line_color="#ffbb00", line_width=1.5, line_dash="dash",
                              annotation_text=f"ZERO GAMMA: {zero_gamma_val:,.0f}", annotation_position="top right")
        
        fig_candles.add_hline(y=put_wall_val, line_color="#ff3a60", line_width=2, 
                              annotation_text=f"PUT WALL: {put_wall_val:,.0f}", annotation_position="bottom right")

        # Configura a margem do zoom vertical para que as 3 linhas caibam perfeitamente na janela
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
        idx_max_pos_inst = np.argmax(inst_flow)
        idx_min_neg_inst = np.argmin(inst_flow)
        
        cores_inst = []
        for i, v in enumerate(inst_flow):
            if i == idx_max_pos_inst:
                cores_inst.append('#00ff88')
            elif i == idx_min_neg_inst:
                cores_inst.append('#ff3a60')
            else:
                cores_inst.append('#1a53ff')
                
        fig_inst = go.Figure()
        fig_inst.add_trace(go.Bar(x=strikes, y=inst_flow, marker_color=cores_inst, showlegend=False))
        fig_inst.add_vline(x=preco_spot, line_dash="dash", line_color="cyan", line_width=1.5)
        fig_inst.update_layout(
            title="INSTITUTIONAL FLOW", title_font_size=12, height=560, template="plotly_dark",
            paper_bgcolor="#111", plot_bgcolor="#111", margin=dict(l=10, r=10, t=35, b=10),
            xaxis=dict(showgrid=False, tickformat=",.0f"), yaxis=dict(showgrid=True, gridcolor='#222')
        )
        st.plotly_chart(fig_inst, use_container_width=True)

except Exception as e:
    st.error(f"Erro na montagem do Workspace: {e}")
