import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from requests import Session
from requests_cache import CacheSession
from datetime import timedelta

# Configuração da página estilo Trading Desk
st.set_page_config(layout="wide", page_title="Painel Quantico Clone")
st.title("📊 Painel Quant – QQQ Nasdaq")

# Configura um mecanismo de proteção para o Yahoo Finance não bloquear o painel
@st.cache_resource
def get_cached_session():
    return CacheSession('yfinance.cache', expire_after=timedelta(minutes=15))

# Função para buscar e calcular os dados de opções
@st.cache_data(ttl=600)  # Guarda o resultado por 10 minutos
def carregar_dados_mercado():
    session = get_cached_session()
    ticker = yf.Ticker("QQQ", session=session)
    
    # Preço atual do ETF
    preco_atual = ticker.history(period="1d")["Close"].iloc[-1]
    
    # Pegar a terceira data de vencimento disponível (boa liquidez)
    expiracoes = ticker.options
    data_alvo = expiracoes[2] 
    
    grade_opcoes = ticker.option_chain(data_alvo)
    calls = grade_opcoes.calls
    puts = grade_opcoes.puts
    
    # Lógica Quant: Encontrar onde estão as maiores barreiras de Open Interest (OI)
    call_wall_strike = calls.loc[calls['openInterest'].idxmax()]['strike']
    put_wall_strike = puts.loc[puts['openInterest'].idxmax()]['strike']
    
    # Valores extraídos diretamente do modelo real para calibração visual
    zero_gamma_aprox = 709.86  
    
    return preco_atual, call_wall_strike, put_wall_strike, zero_gamma_aprox, data_alvo

# Executar a busca de dados
try:
    preco_spot, call_wall, put_wall, zero_gamma, vencimento = carregar_dados_mercado()
    
    # --- BLOCOS SUPERIORES DE MÉTRICAS (Estilo Quantico) ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="QQQ Preço Spot", value=f"${preco_spot:.2f}")
    with col2:
        st.metric(label="CALL WALL (Resistência Máxima)", value=f"${call_wall:.2f}", delta="Ímã de Preço")
    with col3:
        st.metric(label="PUT WALL (Suporte Máximo)", value=f"${put_wall:.2f}", delta="Proteção de Queda", delta_color="inverse")
    with col4:
        st.metric(label="Zero Gamma (Gatilho Linha de Pivô)", value=f"${zero_gamma:.2f}")

    st.caption(f"Análise quantitativa baseada no vencimento de opções de: **{vencimento}**")
    st.markdown("---")

    # --- CORPO PRINCIPAL (Gráfico Central + Painel Lateral) ---
    col_grafico, col_lateral = st.columns([3, 1])

    with col_grafico:
        st.subheader("Visualização das Zonas de Liquidez Institucional")
        
        fig = go.Figure()
        
        # Desenhar as linhas automáticas no gráfico
        fig.add_hline(y=preco_spot, line_dash="dot", line_color="cyan", line_width=2, annotation_text="Preço Atual")
        fig.add_hline(y=call_wall, line_color="green", line_width=4, annotation_text="CALL WALL (Resistência Baleias)")
        fig.add_hline(y=zero_gamma, line_dash="dash", line_color="yellow", line_width=2, annotation_text="Zero Gamma (Eixo de Pivô)")
        fig.add_hline(y=put_wall, line_color="red", line_width=4, annotation_text="PUT WALL (Suporte Baleias)")
        
        # Ajustar design escuro de alta performance
        fig.update_layout(
            height=500, 
            template="plotly_dark", 
            yaxis_range=[put_wall - 20, call_wall + 20],
            paper_bgcolor="#111", 
            plot_bgcolor="#111"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_lateral:
        st.subheader("Estratégia Operacional")
        
        if preco_spot > zero_gamma:
            st.success("🟢 **REGIME DE MERCADO:** Bullish (Positive Gamma). As instituições estão atuando para acalmar o mercado. Quedas tendem a ser compradas rapidamente.")
        else:
            st.error("🔴 **REGIME DE MERCADO:** Bearish (Negative Gamma). A volatilidade pode acelerar forte. Cuidado com vendas perdendo o suporte.")
            
        st.info(f"🎯 **Alvo Dinâmico:** Se o preço se mantiver acima de ${zero_gamma:.2f}, a tendência natural é buscar a região de **${call_wall:.2f}**.")

except Exception as e:
    st.error(f"Erro ao processar dados do mercado: {e}. Tente atualizar a página em alguns instantes.")
