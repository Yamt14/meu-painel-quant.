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
times = [base_time.replace(hour=h, minute=0) for h in range(24)]
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
        increasing_line_color=green_color,
        decreasing_line_color=red_color,
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
