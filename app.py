# app.py
import streamlit as st
import plotly.graph_objects as go
from data_engine import IndianMarketEngine

# 1. Page Configuration
st.set_page_config(page_title="InvestWise India", page_icon="🇮🇳", layout="wide")

# 2. India-Themed Glassmorphism
st.markdown("""
<style>
    .stApp { background: #070a13; color: #f3f4f6; }
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .metric-val { font-size: 1.8rem; font-weight: 800; color: #10b981; }
    .news-card { padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
</style>
""", unsafe_allow_html=True)

st.title("🇮🇳 InvestWise AI : NSE Market Terminal")

# --- QUICK PICKS (NO TYPING REQUIRED) ---
st.markdown("**Nifty 50 Quick Scans:**")
col1, col2, col3, col4, col5 = st.columns(5)
with col1: 
    if st.button("Reliance Ind"): st.session_state.ticker = "RELIANCE"
with col2: 
    if st.button("Tata Motors"): st.session_state.ticker = "TATAMOTORS"
with col3: 
    if st.button("HDFC Bank"): st.session_state.ticker = "HDFCBANK"
with col4: 
    if st.button("Zomato"): st.session_state.ticker = "ZOMATO"
with col5: 
    if st.button("IRFC"): st.session_state.ticker = "IRFC"

# User Input (Defaults to whatever button was clicked, or TATAMOTORS)
if 'ticker' not in st.session_state:
    st.session_state.ticker = "TATAMOTORS"

ticker_input = st.text_input("Or type an Indian Stock Name (e.g. INFY, TCS):", value=st.session_state.ticker)

st.markdown("---")

if ticker_input:
    with st.spinner("Fetching live NSE Data & Breaking News..."):
        profile = IndianMarketEngine.get_stock_profile(ticker_input)
        df_hist = IndianMarketEngine.get_chart_data(ticker_input)
        news = IndianMarketEngine.get_live_indian_news(ticker_input)

    if "error" in profile:
        st.error(profile["error"])
    else:
        # --- TOP KPI METRICS ---
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="glass-card">Market Price<div class="metric-val">₹{profile["current_price"]:,}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="glass-card">Market Cap<div class="metric-val" style="color:#60a5fa;">{profile["market_cap_fmt"]}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="glass-card">P/E Ratio<div class="metric-val" style="color:#f59e0b;">{profile["pe_ratio"]}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="glass-card">ROE<div class="metric-val" style="color:#a855f7;">{profile["roe"]}%</div></div>', unsafe_allow_html=True)

        # --- CHART & NEWS LAYOUT ---
        col_chart, col_news = st.columns([2, 1])

        with col_chart:
            st.markdown(f"### 📈 {profile['name']} (6-Month Trend)")
            if not df_hist.empty:
                fig = go.Figure(data=[go.Candlestick(
                    x=df_hist['Date'], open=df_hist['Open'], high=df_hist['High'],
                    low=df_hist['Low'], close=df_hist['Close'],
                    increasing_line_color='#10b981', decreasing_line_color='#ef4444'
                )])
                fig.update_layout(
                    template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    height=450, margin=dict(l=0, r=0, t=10, b=0),
                    xaxis_rangeslider_visible=False # Removes the bulky slider at the bottom
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Chart data unavailable for this specific ticker today.")

        with col_news:
            st.markdown("### 📰 Live Breaking News (Last 24h)")
            st.caption("Sourced live via Google News India RSS.")
            for item in news:
                st.markdown(f"""
                <div class="news-card">
                    <a href="{item['link']}" target="_blank" style="color:#60a5fa; text-decoration:none; font-weight:600;">{item['title']}</a>
                    <br><span style="font-size:0.8rem; color:#9ca3af;">{item.get('published', 'Just now')}</span>
                </div>
                """, unsafe_allow_html=True)
                
        # --- BUSINESS OVERVIEW ---
        st.markdown("---")
        st.markdown("### 🏢 What Do They Do?")
        st.info(profile['summary'])
