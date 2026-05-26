import streamlit as st
import plotly.graph_objects as go

# Configuração da página para ocupar a tela inteira (Estilo Trading Desk)
st.set_page_config(layout="wide", page_title="Painel de Volatilidade & GEX")
st.title("📊 Painel Quant - Clone QQQ")

# --- DADOS REAIS EXTRAÍDOS DA SUA TELA ---
preco_spot = 717.62
net_gex = "+1.3B"
put_call_ratio = 1.59
call_wall = 730.00
put_wall = 650.00
zero_gamma = 709.86
squeeze_score = 40

# --- INDICADORES DO TOPO (Métricas de Sentimento) ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="QQQ Preço Spot", value=f"${preco_spot}")
with col2:
    st.metric(label="Net GEX", value=net_gex, delta="Ambiente Seguro")
with col3:
    st.metric(label="Put/Call Ratio", value=put_call_ratio)
with col4:
    st.metric(label="Termômetro Squeeze", value=f"{squeeze_score}/100", delta="Possível")

st.markdown("---")

# --- CORPO PRINCIPAL (Gráfico + Painel Lateral) ---
col_grafico, col_lateral = st.columns([3, 1])

with col_grafico:
    st.subheader("Gráfico Central com Barreiras de Opções (GEX)")
    
    # Criando um gráfico simulando o movimento de preço com as linhas do site
    fig = go.Figure()
    
    # Preço Atual
    fig.add_hline(y=preco_spot, line_dash="dot", line_color="blue", annotation_text="Preço Spot")
    # Call Wall (Resistência)
    fig.add_hline(y=call_wall, line_width=3, line_color="green", annotation_text="CALL WALL (Resistência Máxima)")
    # Zero Gamma (Gatilho)
    fig.add_hline(y=zero_gamma, line_width=2, line_color="yellow", annotation_text="Zero Gamma (Gatilho)")
    # Put Wall (Suporte)
    fig.add_hline(y=put_wall, line_width=3, line_color="red", annotation_text="PUT WALL (Suporte Máximo)")
    
    fig.update_layout(height=500, template="plotly_dark", yaxis_range=[630, 750])
    st.plotly_chart(fig, use_container_width=True)

with col_lateral:
    st.subheader("Sinais Operacionais")
    st.info("🟢 **Volatilidade:** FORTE (Movimentos tendem a ser controlados)")
    st.warning("🟡 **Suporte Curto:** Brecha se cair de $709.86")
    st.success("🎯 **Ímã do Preço:** Alvo macro em $730.00")
