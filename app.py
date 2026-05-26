import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import numpy as np

# Configuração da página estilo Trading Desk
st.set_page_config(layout="wide", page_title="Painel Quant – MNQ GEX")
st.title("📊 Painel Quant – MNQ Nasdaq Gamma Exposure")

# Função para buscar dados e simular a curva de barras quantitativas (GEX Profile)
@st.cache_data(ttl=300)
def carregar_estrutura_gex():
    try:
        ticker_futuro = yf.Ticker("NQ=F")
        preco_mnq = ticker_futuro.history(period="1d")["Close"].iloc[-1]
    except:
        preco_mnq = 19898.00
        
    try:
        ticker_qqq = yf.Ticker("QQQ")
        preco_qqq = ticker_qqq.history(period="1d")["Close"].iloc[-1]
    except:
        preco_qqq = 717.62

    fator_conversao = preco_mnq / preco_qqq

    # Barreiras principais extraídas do modelo macro
    call_wall = 730.00 * fator_conversao
    put_wall = 650.00 * fator_conversao
    zero_gamma = 709.86 * fator_conversao
    
    # Gerando a distribuição de Strikes (Degraus de preço ao redor do spot)
    passo = 50  # Variação de pontos no MNQ
    strikes = np.arange(int(put_wall - 500), int(call_wall + 500), passo)
    
    # Criando a simulação matemática das barras de Gamma (Exposição de Volatilidade)
    gamma_values = []
    for s in strikes:
        if abs(s - call_wall) < passo:
            val = 450000000  # Pico de Call Gamma (Barra verde gigante)
        elif abs(s - put_wall) < passo:
            val = -380000000  # Pico de Put Gamma (Barra vermelha de suporte)
        elif abs(s - zero_gamma) < passo:
            val = 10000000   # Próximo a zero
        elif s > zero_gamma:
            # Distribuição normal positiva para calls
            val = np.random.randint(20000000, 150000000)
        else:
            # Distribuição negativa para puts
            val = -np.random.randint(20000000, 180000000)
        gamma_values.append(val)
        
    return preco_mnq, call_wall, put_wall, zero_gamma, strikes, gamma_values

try:
    preco_spot, call_wall, put_wall, zero_gamma, strikes, gamma_values = carregar_estrutura_gex()
    
    # --- BLOCOS SUPERIORES DE MÉTRICAS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="MNQ Preço Atual", value=f"{preco_spot:,.2f}")
    with col2:
        st.metric(label="CALL WALL (Resistência)", value=f"{call_wall:,.2f}")
    with col3:
        st.metric(label="PUT WALL (Suporte)", value=f"{put_wall:,.2f}")
    with col4:
        st.metric(label="Zero Gamma (Pivô)", value=f"{zero_gamma:,.2f}")

    st.markdown("---")

    # --- CORPO PRINCIPAL ---
    col_grafico, col_lateral = st.columns([3, 1])

    with col_grafico:
        st.subheader("Strike Profile – Perfil de Exposição de Gamma (GEX)")
        
        # Separando cores das barras: verde para positivo, vermelho para negativo
        cores_barras = ['#00ffc2' if v >= 0 else '#ff3a60' for v in gamma_values]
        
        fig = go.Figure()
        
        # 1. Desenha o Gráfico de Barras do Perfil Quantitativo
        fig.add_trace(go.Bar(
            x=strikes,
            y=gamma_values,
            marker_color=cores_barras,
            name="Exposição de Gamma",
            hovertemplate="Strike: %{x}<br>GEX: %{y:,.0f}"
        ))
        
        # 2. Desenha linhas de marcação verticais para balizar onde estão os muros no preço
        fig.add_vline(x=preco_spot, line_dash="dot", line_color="cyan", line_width=2, annotation_text="Preço Spot")
        fig.add_vline(x=call_wall, line_color="green", line_width=2, annotation_text="Call Wall")
        fig.add_vline(x=put_wall, line_color="red", line_width=2, annotation_text="Put Wall")
        
        # Estilização profissional idêntica ao tema Dark institucional
        fig.update_layout(
            height=580,
            template="plotly_dark",
            paper_bgcolor="#111",
            plot_bgcolor="#111",
            xaxis_title="Nível de Preço / Strikes do MNQ",
            yaxis_title="Exposição Líquida de Gamma ($)",
            margin=dict(l=10, r=10, t=30, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)

    with col_lateral:
        st.subheader("Análise Quântica")
        
        if preco_spot > zero_gamma:
            st.success("🟢 **REGIME LONG GAMMA:** O mercado está acima do eixo de pivô. Os Market Makers atuam contra a volatilidade. Movimentos tendem a consolidar ou subir devagar em direção à Call Wall.")
        else:
            st.error("🔴 **REGIME SHORT GAMMA:** Zona de risco de aceleração. Abaixo do Pivô, as instituições precisam vender contratos para se proteger, acelerando os movimentos de queda.")
            
        st.markdown("### 📊 Níveis Operacionais")
        st.info(f"🚀 **Call Wall:** Bloqueio vendedor nos **{call_wall:,.0f}** pontos.")
        st.warning(f"⚡ **Pivô:** Inversão de fluxo nos **{zero_gamma:,.0f}** pontos.")
        st.error(f"🛡️ **Put Wall:** Defesa compradora extrema nos **{put_wall:,.0f}** pontos.")

except Exception as e:
    st.error(f"Erro ao processar estrutura quântica: {e}")
