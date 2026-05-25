import streamlit as st
import yfinance as yf
import streamlit.components.v1 as components

# Configuração da página estilo Trading Desk
st.set_page_config(layout="wide", page_title="Painel Quant – MNQ TradingView")
st.title("📊 Painel Quant – MNQ Nasdaq Live TradingView")

# Função para buscar os dados macros e calcular as barreiras no MNQ
@st.cache_data(ttl=900)
def calcular_barreiras_mnq():
    try:
        ticker_futuro = yf.Ticker("NQ=F")
        preco_mnq = ticker_futuro.history(period="1d")["Close"].iloc[-1]
    except:
        preco_mnq = 19896.25  # Valor de backup
        
    try:
        ticker_qqq = yf.Ticker("QQQ")
        preco_qqq = ticker_qqq.history(period="1d")["Close"].iloc[-1]
    except:
        preco_qqq = 717.62

    # Fator de conversão dinâmico
    fator_conversao = preco_mnq / preco_qqq

    # Barreiras extraídas do modelo de opções do QQQ
    call_wall_qqq = 730.00
    put_wall_qqq = 650.00
    zero_gamma_qqq = 709.86
    
    # Conversão para escala de pontos do contrato futuro
    call_wall_mnq = call_wall_qqq * fator_conversao
    put_wall_mnq = put_wall_qqq * fator_conversao
    zero_gamma_mnq = zero_gamma_qqq * fator_conversao
    
    return preco_mnq, call_wall_mnq, put_wall_mnq, zero_gamma_mnq

try:
    preco_spot, call_wall, put_wall, zero_gamma = calcular_barreiras_mnq()
    
    # --- BLOCOS SUPERIORES DE MÉTRICAS ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="MNQ Preço de Referência", value=f"{preco_spot:,.2f}")
    with col2:
        st.metric(label="CALL WALL (Resistência Alvo)", value=f"{call_wall:,.2f}")
    with col3:
        st.metric(label="PUT WALL (Suporte Crítico)", value=f"{put_wall:,.2f}")
    with col4:
        st.metric(label="Zero Gamma (Eixo de Pivô)", value=f"{zero_gamma:,.2f}")

    st.markdown("---")

    # --- CORPO PRINCIPAL ---
    col_grafico, col_lateral = st.columns([3, 1])

    with col_grafico:
        st.subheader("Gráfico Profissional TradingView (Tempo Real - 5m)")
        
        # Widget atualizado com a exchange oficial CME e o contrato Micro MNQ1!
        tradingview_widget = """
        <div class="tradingview-widget-container" style="height:700px; width:100%;">
          <div id="tradingview_nasdaq" style="height:700px;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({
            "width": "100%",
            "height": 700,
            "symbol": "CME:MNQ1!",
            "interval": "5",
            "timezone": "America/New_York",
            "theme": "dark",
            "style": "1",
            "locale": "br",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_nasdaq"
          });
          </script>
        </div>
        """
        components.html(tradingview_widget, height=720)

    with col_lateral:
        st.subheader("Estrategia Operacional")
        
        if preco_spot > zero_gamma:
            st.success("🟢 **REGIME DE FLUXO:** Comprador (Positive Gamma). Mercado trabalhando na zona de proteção institucional. Quedas tendem a ser defendidas.")
        else:
            st.error("🔴 **REGIME DE FLUXO:** Vendedor (Negative Gamma). O preço perdeu o pivô macro. A volatilidade intradiária tende a acelerar forte.")
            
        st.info("💡 **Dica de Execução:** Use as ferramentas de desenho do TradingView ao lado para traçar três linhas horizontais permanentes nas coordenadas indicadas nas métricas acima.")

        st.markdown("### 📋 Alvos Balizadores")
        st.write(f"🎯 **Resistência Máxima:** `{call_wall:,.0f}`")
        st.write(f"⚖️ **Pivô do Dia:** `{zero_gamma:,.0f}`")
        st.write(f"🛡️ **Suporte Máximo:** `{put_wall:,.0f}`")

except Exception as e:
    st.error(f"Erro ao carregar os componentes do painel: {e}")
