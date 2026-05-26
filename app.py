import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Painel Quantico Clone")
st.title("📊 Painel Quant – QQQ Nasdaq")

@st.cache_data(ttl=300)
def carregar_dados_mercado():
    ticker = yf.Ticker("QQQ")
    preco_atual = ticker.history(period="1d")["Close"].iloc[-1]
    expiracoes = ticker.options
    data_alvo = expiracoes[2] 
    grade_opcoes = ticker.option_chain(data_alvo)
    calls = grade_opcoes.calls
    puts = grade_opcoes.puts
    
    call_wall_strike = calls.loc[calls['openInterest'].idxmax()]['strike']
    put_wall_strike = puts.loc[puts['openInterest'].idxmax()]['strike']
    zero_gamma_aprox = (call_wall_strike + put_wall_strike) / 2
    
    return preco_atual, call_wall_strike, put_wall_strike, zero_gamma_aprox, data_alvo

try:
    preco_spot, call_wall, put_wall, zero_gamma, vencimento = carregar_dados_mercado()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="QQQ Preço Spot", value=f"${preco_spot:.2f}")
    with col2:
        st.metric(label="CALL WALL (Resistência)", value=f"${call_wall:.2f}")
    with col3:
        st.metric(label="PUT WALL (Suporte)", value=f"${put_wall:.2f}")
    with col4:
        st.metric(label="Zero Gamma (Pivô)", value=f"${zero_gamma:.2f}")

    st.markdown("---")
    
    fig = go.Figure()
    fig.add_hline(y=preco_spot, line_dash="dot", line_color="blue", line_width=2, annotation_text="Preço Spot")
    fig.add_hline(y=call_wall, line_color="green", line_width=4, annotation_text="CALL WALL")
    fig.add_hline(y=zero_gamma, line_dash="dash", line_color="yellow", line_width=2, annotation_text="Zero Gamma")
    fig.add_hline(y=put_wall, line_color="red", line_width=4, annotation_text="PUT WALL")
    
    fig.update_layout(height=500, template="plotly_dark", yaxis_range=[put_wall - 15, call_wall + 15])
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
