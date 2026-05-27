import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from datetime import datetime

# 1. Configuração da página e Título
st.set_page_config(layout="wide", page_title="Painel Quant Pro")
st.title("Painel Quant Pro")

# 2. Dados Fictícios Estáveis (Simulando 26 de Maio de 2026)
base_time = datetime(2026, 5, 26)
times = [base_time.replace(hour=h, minute=0)import streamlit as st
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
        st.metric(label="MNQ Preço Atual", value=f"{preco_spot:,.2f}")
    with col2:
        st.metric(label="CALL WALL (Resistência)", value=f"{call_wall_val:,.2f}")
    with col3:
        st.metric(label="PUT WALL (Suporte)", value=f"{put_wall_val:,.2f}")
    with col4:
        st.metric(label="Zero Gamma (Pivô)", value=f"{zero_gamma_val:,.2f}")

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
    st.error(f"Erro na montagem do Workspace: {e}") for h in range(24)]
prices_fictitious = np.linspace(29800, 30200, 24)
prices_fictitious += np.random.normal(0, 50, 24) # Adiciona um pouco de "ruído"
spot_price_fictitious = 30144.25

# Simulação de um mini-histórico para os candles
candles_fictitious = pd.DataFrame({
    'Open': prices_fictitious - 10,
    'High': prices_fictitious + 20,
    'Low': prices_fictitious - 25,
    'Close': prices_fictitious,
}, index=times)

# Dados de strikes fictícios
strikes_fictitious = np.arange(29800, 30500, 50)
delta_gex_fictitious = np.random.normal(0, 0.003, len(strikes_fictitious))
time_pressure_fictitious = np.random.normal(0, 0.005, len(strikes_fictitious))
inst_flow_fictitious = np.random.normal(0, 0.008, len(strikes_fictitious))

# Funções auxiliares para destaques
def get_highlight_indices(data, n=1):
    # Encontra os índices dos 'n' maiores e 'n' menores valores
    sorted_indices = np.argsort(data)
    return np.concatenate([sorted_indices[:n], sorted_indices[-n:]])

def create_bar_chart(x, y, title, highlight_indices, spot_price):
    # Cria uma lista de cores, definindo uma cor especial para destaques
    base_color = 'rgb(31, 119, 180)' # Azul padrão
    highlight_color = 'rgb(0, 255, 255)' # Ciano brilhante
    colors = [base_color] * len(y)
    for idx in highlight_indices:
        colors[idx] = highlight_color
    
    fig = go.Figure(go.Bar(
        x=x, y=y,
        marker_color=colors,
        name=title,
        xaxis='x',
        yaxis='y'
    ))
    
    # Adiciona linha tracejada para o preço spot
    fig.add_vline(x=spot_price, line_dash="dash", line_color=highlight_color)
    
    fig.update_layout(
        title=title,
        xaxis_title="Strikes",
        template="plotly_dark",
        margin=dict(l=10, r=10, t=35, b=10),
        xaxis=dict(showgrid=True, gridcolor='#222', tickmode='array', tickvals=[29.8e3, 30e3, 30.1e3, 30.2e3, 30.3e3], ticktext=['29.8k','30k','30.1k','30.2k','30.3k']),
        yaxis=dict(showgrid=True, gridcolor='#222')
    )
    return fig

def create_candlestick_chart(df, spot_price, highlight_indices, title):
    # Destaque de marcadores nos preços máximos e mínimos
    # Neste exemplo fictício, destacamos o primeiro e último candle para demonstração
    
    blue_color = 'rgb(31, 119, 180)' # Azul único para todos os candles
    highlight_color = 'rgb(0, 255, 255)' # Ciano brilhante para marcadores
    
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color=blue_color,
        decreasing_line_color=blue_color,
        name=title
    )])
    
    # Adiciona marcadores de destaque
    highlight_times = df.index[highlight_indices]
    highlight_prices = df['Close'].iloc[highlight_indices]
    
    fig.add_trace(go.Scatter(
        x=highlight_times,
        y=highlight_prices,
        mode='markers',
        marker=dict(color=highlight_color, size=10, symbol='diamond'),
        name='Ponto de Interesse'
    ))
    
    # Adiciona marcadores nos extremos de preço para o gráfico de linhas inferior
    # Para o gráfico fictício, usamos o primeiro e último ponto.
    low_price_idx = np.argmin(df['Low'])
    high_price_idx = np.argmax(df['High'])
    
    fig.update_layout(
        title=title,
        xaxis_title="Tempo (Fictício)",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        margin=dict(l=10, r=10, t=35, b=10),
        xaxis=dict(showgrid=True, gridcolor='#222'),
        yaxis=dict(showgrid=True, gridcolor='#222', tickmode='array', tickvals=[29.8e3, 29.9e3, 30e3, 30.1e3], ticktext=['29.8k','29.9k','30k','30.1k'])
    )
    return fig

def create_line_chart(df, title, highlight_indices):
    blue_color = 'rgb(31, 119, 180)'
    highlight_color = 'rgb(0, 255, 255)'
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        line=dict(color=blue_color, width=2),
        name=title
    ))
    
    # Adiciona marcadores de destaque
    highlight_times = df.index[highlight_indices]
    highlight_prices = df['Close'].iloc[highlight_indices]
    
    fig.add_trace(go.Scatter(
        x=highlight_times,
        y=highlight_prices,
        mode='markers',
        marker=dict(color=highlight_color, size=8, symbol='circle'),
        name='Estremo'
    ))
    
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False), # Oculta o eixo X
        yaxis=dict(visible=False), # Oculta o eixo Y
    )
    return fig

# --- BLOCO SUPERIORES DE MÉTRICAS ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="MNQ ATUAL", value="$30,144.25")
with col2:
    st.metric(label="CALL WALL", value="$30,264.25")
with col3:
    st.metric(label="PUT WALL", value="$29,994.25")
with col4:
    st.metric(label="ZERO GAMMA", value="$30,119.25")

st.markdown("---")

# --- LAYOUT DE GRÁFICOS ---
col_esquerda, col_centro, col_direita = st.columns([1, 2, 1])

# --- COLUNA ESQUERDA: DELTA HEDGING & TIME PRESSURE ---
with col_esquerda:
    # 1. DELTA HEDGING (Destaque para o maior e menor)
    delta_highlight = get_highlight_indices(delta_gex_fictitious, n=1)
    fig_delta = create_bar_chart(strikes_fictitious, delta_gex_fictitious, "DELTA HEDGING", delta_highlight, spot_price_fictitious)
    st.plotly_chart(fig_delta, use_container_width=True)

    # 2. TIME PRESSURE (Destaque para o maior e menor)
    time_highlight = get_highlight_indices(time_pressure_fictitious, n=1)
    fig_time = create_bar_chart(strikes_fictitious, time_pressure_fictitious, "TIME PRESSURE", time_highlight, spot_price_fictitious)
    st.plotly_chart(fig_time, use_container_width=True)

# --- COLUNA CENTRAL: CANDLESTICK & LINHA ---
with col_centro:
    # 3. CANDLESTICK REAL-TIME (Destaque para extremos de tempo e preço)
    low_price_idx = np.argmin(candles_fictitious['Low'])
    high_price_idx = np.argmax(candles_fictitious['High'])
    candles_highlight = [0, len(candles_fictitious)-1] # Exemplo: Destaque de tempo
    
    fig_candles = create_candlestick_chart(candles_fictitious, spot_price_fictitious, candles_highlight, "CANDLESTICK REAL-TIME")
    st.plotly_chart(fig_candles, use_container_width=True)
    
    # 4. GRÁFICO DE LINHA INFERIOR (Destaque para pontos-chave)
    # Exemplo: Destaque do primeiro e último ponto
    line_highlight = [0, len(candles_fictitious)-1]
    fig_line = create_line_chart(candles_fictitious, "Trend", line_highlight)
    st.plotly_chart(fig_line, use_container_width=True)

# --- COLUNA DIREITA: INSTITUTIONAL FLOW ---
with col_direita:
    # 5. INSTITUTIONAL FLOW (Destaque para o maior e menor)
    flow_highlight = get_highlight_indices(inst_flow_fictitious, n=1)
    fig_flow = create_bar_chart(strikes_fictitious, inst_flow_fictitious, "INSTITUTIONAL FLOW", flow_highlight, spot_price_fictitious)
    st.plotly_chart(fig_flow, use_container_width=True)
