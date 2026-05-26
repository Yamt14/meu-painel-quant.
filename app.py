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
    col1, col2, col3, col4 , col5= st.columns(5)
    with col1:
        st.metric(label="MNQ Preço Atual (Pontos)", value=f"{preco_spot:,.2f}")
    with col2:
        st.metric(label="CALL WALL (Resistência Alvo)", value=f"{call_wall:,.2f}", delta="Ímã Institucional")
    with col3:
        st.metric(label="PUT WALL (Suporte Crítico)", value=f"{put_wall:,.2f}", delta="Zona de Defesa", delta_color="inverse")
    with col4:
        st.metric(label="Zero Gamma (Eixo de Pivô)", value=f"{zero_gamma:,.2f}")
         with col5:
        st.metric(label="Strategy MNQ ",
                  if preco_spot > zero_gamma:
            st.success("🟢 **REGIME DE FLUXO:** Comprador (Positive Gamma). Os contratos futuros estão trabalhando na zona de proteção das instituições. Viés de alta para buscar as resistências.")
            st.info(f"🎯 **Alvo de Pontos:** Mantendo-se acima de {zero_gamma:,.0f} pontos, o índice futuro busca estruturalmente a região de {call_wall:,.0f} pontos.")
        else:
            st.error("🔴 **REGIME DE FLUXO:** Vendedor (Negative Gamma). O preço perdeu o pivô quantitativo. Movimentos de queda tendem a acelerar rápido.")
            st.warning(f"⚠️ **Risco Extremo:** Se o mercado acelerar abaixo de {zero_gamma:,.0f}, o suporte principal de longo prazo está apenas em {put_wall:,.0f} pontos.")
{zero_gamma:,.2f}")
   

    st.caption("Análise quantitativa baseada na estrutura do mercado de opções convertida para o mercado futuro.")
    st.markdown("---")

    # --- CORPO PRINCIPAL (Gráfico Central + Painel Lateral) ---
    col_grafico, col_lateral = st.columns([3, 1])

    with col_grafico:
        st.subheader("Zonas de Liquidez e Alvos de Volatilidade no MNQ")
        
        fig = go.Figure()
        
        # Desenhar as linhas de pontuação do mercado futuro
        fig.add_hline(y=preco_spot, line_dash="dot", line_color="cyan", line_width=2, annotation_text="Preço MNQ Atual")
        fig.add_hline(y=call_wall, line_color="green", line_width=4, annotation_text="CALL WALL (Barreira Vendedora)")
        fig.add_hline(y=zero_gamma, line_dash="dash", line_color="yellow", line_width=2, annotation_text="Zero Gamma")
        fig.add_hline(y=put_wall, line_color="red", line_width=4, annotation_text="PUT WALL (Barreira Compradora)")
        
        # Ajustar o zoom do gráfico ao redor dos pontos do MNQ
        fig.update_layout(
            height=500, 
            template="plotly_dark", 
            yaxis_range=[put_wall - 500, call_wall + 500],
            paper_bgcolor="#111", 
            plot_bgcolor="#111"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_lateral:
        st.subheader("Estratégia MNQ")
        
        if preco_spot > zero_gamma:
            st.success("🟢 **REGIME DE FLUXO:** Comprador (Positive Gamma). Os contratos futuros estão trabalhando na zona de proteção das instituições. Viés de alta para buscar as resistências.")
            st.info(f"🎯 **Alvo de Pontos:** Mantendo-se acima de {zero_gamma:,.0f} pontos, o índice futuro busca estruturalmente a região de {call_wall:,.0f} pontos.")
        else:
            st.error("🔴 **REGIME DE FLUXO:** Vendedor (Negative Gamma). O preço perdeu o pivô quantitativo. Movimentos de queda tendem a acelerar rápido.")
            st.warning(f"⚠️ **Risco Extremo:** Se o mercado acelerar abaixo de {zero_gamma:,.0f}, o suporte principal de longo prazo está apenas em {put_wall:,.0f} pontos.")

except Exception as e:
    st.error(f"Erro ao processar dados do MNQ: {e}. Atualize a página em alguns instantes.")
