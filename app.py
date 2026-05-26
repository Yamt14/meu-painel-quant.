import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# Configuração da página estilo Trading Desk
st.set_page_config(layout="wide", page_title="Painel Quant – MNQ Nasdaq")
st.title("📊 Painel Quant – MNQ Nasdaq Futuros")

# Função para buscar os dados e fazer a conversão matemática para o MNQ
@st.cache_data(ttl=900)  # Guarda o resultado por 15 minutos para evitar bloqueios
def carregar_dados_mnq():
    # 1. Puxamos o preço real do contrato futuro do Nasdaq (Ticker: NQ=F)
    try:
        ticker_futuro = yf.Ticker("NQ=F")
        preco_mnq = ticker_futuro.history(period="1d")["Close"].iloc[-1]
    except:
        preco_mnq = 19850.00  # Valor de backup caso a API falhe
        
    # 2. Puxamos o preço do QQQ para calcular o fator de proporção exato
    try:
        ticker_qqq = yf.Ticker("QQQ")
        preco_qqq = ticker_qqq.history(period="1d")["Close"].iloc[-1]
    except:
        preco_qqq = 717.54

    # Fator de conversão (Ex: Se o NQ está 19850 e o QQQ está 717.54, o fator é ~27.66)
    fator_conversao = preco_mnq / preco_qqq

    # 3. Pegamos as barreiras institucionais do QQQ (InsiderFinance) e convertemos para o MNQ
    call_wall_qqq = 730.00
    put_wall_qqq = 650.00
    zero_gamma_qqq = 709.86
    
    # Aplicação do fator quant nos pontos do MNQ
    call_wall_mnq = call_wall_qqq * fator_conversao
    put_wall_mnq = put_wall_qqq * fator_conversao
    zero_gamma_mnq = zero_gamma_qqq * fator_conversao
    
    return preco_mnq, call_wall_mnq, put_wall_mnq, zero_gamma_mnq

# Executar a busca de dados
try:
    preco_spot, call_wall, put_wall, zero_gamma = carregar_dados_mnq()
    
    # --- BLOCOS SUPERIORES DE MÉTRICAS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="MNQ Preço Atual (Pontos)", value=f"{preco_spot:,.2f}")
    with col2:
        st.metric(label="CALL WALL (Resistência Alvo)", value=f"{call_wall:,.2f}", delta="Ímã Institucional")
    with col3:
        st.metric(label="PUT WALL (Suporte Crítico)", value=f"{put_wall:,.2f}", delta="Zona de Defesa", delta_color="inverse")
    with col4:
        st.metric(label="Zero Gamma (Eixo de Pivô)", value=f"{zero_gamma:,.2f}")

    st.caption("Análise quantitativa baseada na estrutura do mercado de opções convertida para o mercado futuro.")
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
