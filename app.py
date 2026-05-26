import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da página estilo Trading Desk
st.set_page_config(layout="wide", page_title="Painel Quant – MNQ 5m")
st.title("📊 Painel Quant – MNQ Nasdaq 5 Minutos")

# Função para buscar os dados intradiários de 5m e fazer a conversão para o MNQ
@st.cache_data(ttl=60)  # Atualiza a cada 1 minuto para o tempo gráfico de 5m ficar ágil
def carregar_dados_mnq_5m():
    # 1. Puxamos o histórico intradiário do contrato futuro
    ticker_futuro = yf.Ticker("NQ=F")
    
    try:
        # Tenta puxar o dia atual em 5 minutos
        df_futuro = ticker_futuro.history(period="1d", interval="5m")
        if df_futuro.empty or len(df_futuro) < 5:
            # Se o dia atual estiver vazio (mercado fechado/parado), puxa os últimos 5 dias para ter velas reais
            df_futuro = ticker_futuro.history(period="5d", interval="5m")
        preco_mnq = df_futuro["Close"].iloc[-1]
    except:
        # Se a API falhar completamente, usamos dados históricos mais estáveis de 1 dia como último recurso
        df_futuro = ticker_futuro.history(period="1mo", interval="1d").tail(30)
        preco_mnq = df_futuro["Close"].iloc[-1]
        
    # 2. Puxamos o preço do QQQ para calcular o fator de proporção exato
    try:
        ticker_qqq = yf.Ticker("QQQ")
        preco_qqq = ticker_qqq.history(period="1d")["Close"].iloc[-1]
    except:
        preco_qqq = 717.62

    # Fator de conversão dinâmico
    fator_conversao = preco_mnq / preco_qqq

    # 3. Barreiras institucionais do QQQ baseadas no InsiderFinance
    call_wall_qqq = 730.00
    put_wall_qqq = 650.00
    zero_gamma_qqq = 709.86
    
    call_wall_mnq = call_wall_qqq * fator_conversao
    put_wall_mnq = put_wall_qqq * fator_conversao
    zero_gamma_mnq = zero_gamma_qqq * fator_conversao
    
    return preco_mnq, call_wall_mnq, put_wall_mnq, zero_gamma_mnq, df_futuro

# Executar a busca de dados
try:
    preco_spot, call_wall, put_wall, zero_gamma, df_historico = carregar_dados_mnq_5m()
    
    # --- BLOCOS SUPERIORES DE MÉTRICAS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="MNQ Preço Atual", value=f"{preco_spot:,.2f}")
    with col2:
        st.metric(label="CALL WALL (Resistência Máxima)", value=f"{call_wall:,.2f}", delta="Ímã Quântico")
    with col3:
        st.metric(label="PUT WALL (Suporte Crítico)", value=f"{put_wall:,.2f}", delta="Zona de Defesa", delta_color="inverse")
    with col4:
        st.metric(label="Zero Gamma (Linha de Pivô)", value=f"{zero_gamma:,.2f}")

    st.caption("Gráfico dinâmico calibrado com as estruturas macro do mercado de opções.")
    st.markdown("---")

    # --- CORPO PRINCIPAL (Gráfico Central + Painel Lateral) ---
    col_grafico, col_lateral = st.columns([3, 1])

    with col_grafico:
        st.subheader("Candlesticks do Mercado Futuro")
        
        # Criando o painel duplo: Candles (topo) e Volume (rodapé)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.03, row_heights=[0.8, 0.2])
        
        # Adicionando as velas
        fig.add_trace(go.Candlestick(
            x=df_historico.index,
            open=df_historico['Open'],
            high=df_historico['High'],
            low=df_historico['Low'],
            close=df_historico['Close'],
            name="MNQ",
            increasing_line_color='#00ffc2', decreasing_line_color='#ff3a60'
        ), row=1, col=1)
        
        # Adicionando o volume no rodapé
        fig.add_trace(go.Bar(
            x=df_historico.index,
            y=df_historico['Volume'],
            name="Volume",
            marker_color='#333',
            showlegend=False
        ), row=2, col=1)
        
        # Desenhando as linhas horizontais de barreiras institucionais
        fig.add_hline(y=call_wall, line_color="green", line_width=3, annotation_text="CALL WALL", row=1, col=1)
        fig.add_hline(y=zero_gamma, line_dash="dash", line_color="yellow", line_width=2, annotation_text="Zero Gamma", row=1, col=1)
        fig.add_hline(y=put_wall, line_color="red", line_width=3, annotation_text="PUT WALL", row=1, col=1)
        
        # Ajuste inteligente de escala dinâmica do Eixo Y
        y_min = df_historico['Low'].min()
        y_max = df_historico['High'].max()
        
        # Customização estética do layout em modo escuro
        fig.update_layout(
            height=650,
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            paper_bgcolor="#111",
            plot_bgcolor="#111",
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        # Força o zoom do gráfico a focar apenas na variação real das velas
        fig.update_yaxes(range=[y_min - 30, y_max + 30], row=1, col=1)
        
        st.plotly_chart(fig, use_container_width=True)

    with col_lateral:
        st.subheader("Análise Operacional 5m")
        
        if preco_spot > zero_gamma:
            st.success("🟢 **MERCADO EM ALTA (Positive Gamma):** O preço do MNQ está trabalhando acima do pivô quant. Favorece operações de compra de curto prazo em suportes dos 5 minutos.")
            st.info(f"🎯 **Alvo Intradiário:** O viés macro é de alta mirando as resistências superiores em direção a {call_wall:,.0f} pontos.")
        else:
            st.error("🔴 **MERCADO EM QUEDA (Negative Gamma):** O preço perdeu o pivô. A volatilidade intradiária tende a aumentar. Pense duas vezes antes de caçar fundos.")
            st.warning(f"⚠️ **Risco:** Abaixo de {zero_gamma:,.0f} pontos, o mercado abre espaço para correções severas.")

except Exception as e:
    st.error(f"Erro ao processar dados do MNQ: {e}. Tente atualizar o painel.")
