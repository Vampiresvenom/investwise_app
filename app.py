import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="InvestWise India", page_icon="🇮🇳", layout="wide")

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
    .val-green { color: #10b981; font-size: 1.6rem; font-weight: 800; }
    .val-blue { color: #60a5fa; font-size: 1.6rem; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

st.title("🇮🇳 InvestWise AI: Market Terminal")
st.caption("Institutional Grade Equities, Mutual Funds, and IPO Research")

# --- TRIPLE ENGINE TABS ---
tab1, tab2, tab3 = st.tabs(["📈 Equities & AI", "🏦 Mutual Funds (Live NAV)", "📄 IPO DRHP Scanner"])

# ==========================================
# TAB 1: EQUITIES ENGINE
# ==========================================
with tab1:
    st.markdown("### NSE Equity Deep Dive")
    ticker_input = st.text_input("Enter Indian Stock Symbol (e.g., TATAMOTORS, ZOMATO, INFY):", value="TATAMOTORS")
    
    if ticker_input:
        # Auto-append NSE suffix if missing
        symbol = ticker_input.upper().strip()
        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            symbol += ".NS"
            
        with st.spinner("Bypassing firewalls to fetch live NSE Data..."):
            try:
                ticker = yf.Ticker(symbol)
                # Using .history() and .fast_info bypasses the cloud blocks that crash .info()
                hist = ticker.history(period="6mo")
                
                if hist.empty:
                    st.error(f"Could not load data for {symbol}. Ensure it is a valid NSE/BSE ticker.")
                else:
                    current_price = hist['Close'].iloc[-1]
                    # Format Market Cap to Indian Crores
                    raw_mcap = ticker.fast_info.market_cap
                    mcap_cr = f"₹{raw_mcap / 10_000_000:,.2f} Cr" if raw_mcap else "N/A"
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.markdown(f'<div class="glass-card">Live Price<br><span class="val-green">₹{current_price:,.2f}</span></div>', unsafe_allow_html=True)
                    with c2:
                        st.markdown(f'<div class="glass-card">Market Cap<br><span class="val-blue">{mcap_cr}</span></div>', unsafe_allow_html=True)
                    with c3:
                        st.markdown(f'<div class="glass-card">52W High<br><span class="val-green">₹{ticker.fast_info.year_high:,.2f}</span></div>', unsafe_allow_html=True)
                    
                    # Clean Charting (Removes empty weekends)
                    hist.reset_index(inplace=True)
                    hist['Date'] = pd.to_datetime(hist['Date']).dt.strftime('%Y-%m-%d')
                    
                    fig = go.Figure(data=[go.Candlestick(
                        x=hist['Date'], open=hist['Open'], high=hist['High'],
                        low=hist['Low'], close=hist['Close'],
                        increasing_line_color='#10b981', decreasing_line_color='#ef4444'
                    )])
                    fig.update_layout(
                        title=f"{symbol} - 6 Month Trend", template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        height=400, xaxis_rangeslider_visible=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"System Error: {str(e)}")

# ==========================================
# TAB 2: MUTUAL FUNDS ENGINE
# ==========================================
with tab2:
    st.markdown("### Real-Time Mutual Fund NAV & History")
    st.caption("Powered directly by the AMFI (Association of Mutual Funds in India) database.")
    
    mf_query = st.text_input("Search Fund (e.g., Parag Parikh, HDFC Small Cap, Quant):")
    
    if mf_query:
        with st.spinner("Searching AMFI Database..."):
            try:
                # Direct API call to Indian Government MF database
                url = f"https://api.mfapi.in/mf/search?q={mf_query}"
                search_results = requests.get(url).json()
                
                if not search_results:
                    st.warning("No mutual funds found matching that name.")
                else:
                    options = {f"{item['schemeCode']} - {item['schemeName']}": item['schemeCode'] for item in search_results[:10]}
                    selected_fund = st.selectbox("Select exact fund variant:", list(options.keys()))
                    
                    if selected_fund:
                        fund_code = options[selected_fund]
                        nav_data = requests.get(f"https://api.mfapi.in/mf/{fund_code}").json()
                        
                        if 'data' in nav_data and nav_data['data']:
                            df_mf = pd.DataFrame(nav_data['data'])
                            df_mf['date'] = pd.to_datetime(df_mf['date'], format='%d-%m-%Y')
                            df_mf['nav'] = df_mf['nav'].astype(float)
                            df_mf = df_mf.sort_values('date')
                            
                            latest_nav = df_mf['nav'].iloc[-1]
                            latest_date = df_mf['date'].iloc[-1].strftime('%d %b %Y')
                            
                            st.markdown(f'<div class="glass-card">Current NAV (As of {latest_date})<br><span class="val-blue">₹{latest_nav:,.4f}</span></div>', unsafe_allow_html=True)
                            
                            fig_mf = go.Figure(data=go.Scatter(
                                x=df_mf['date'], y=df_mf['nav'],
                                mode='lines', line=dict(color='#3b82f6', width=2)
                            ))
                            fig_mf.update_layout(
                                title="Historical NAV Performance", template="plotly_dark",
                                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                height=400
                            )
                            st.plotly_chart(fig_mf, use_container_width=True)
            except Exception as e:
                st.error("Error connecting to AMFI database.")

# ==========================================
# TAB 3: IPO & DRHP AI SCANNER
# ==========================================
with tab3:
    st.markdown("### 📄 IPO Draft Prospectus (DRHP) Risk Scanner")
    st.caption("Paste excerpts from the 'Objects of the Issue' or 'Risk Factors' section of an upcoming IPO to scan for institutional red flags.")

    drhp_text = st.text_area("Paste DRHP Text Segment Here:", height=200)

    if st.button("Scan Prospectus Text", type="primary"):
        if drhp_text:
            text_lower = drhp_text.lower()
            red_flags = []
            positive_signals = []

            # Hardcoded logic checking for classic IPO red flags
            if "repay debt" in text_lower or "repayment of loan" in text_lower or "repayment of certain borrowings" in text_lower:
                red_flags.append("Debt Repayment: Funds are going to lenders rather than directly scaling the business.")
            if "offer for sale" in text_lower or "ofs" in text_lower:
                red_flags.append("Offer for Sale (OFS): Existing promoters or VCs are cashing out. This does not bring fresh capital into the company.")
            if "litigation" in text_lower or "legal proceedings" in text_lower:
                red_flags.append("Litigation Risk: The company has disclosed unresolved legal or regulatory proceedings.")
            if "working capital" in text_lower:
                positive_signals.append("Operational Fuel: A portion of funds is allocated to daily working capital.")
            if "capital expenditure" in text_lower or "manufacturing facility" in text_lower or "expansion" in text_lower:
                positive_signals.append("Growth Capital: Money is targeted at building hard assets or expanding capacity.")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 🚨 Identified Red Flags")
                if red_flags:
                    for flag in red_flags: st.error(flag)
                else:
                    st.success("No major red flags detected in this text block.")
            with c2:
                st.markdown("#### 🟢 Positive Signals")
                if positive_signals:
                    for pos in positive_signals: st.success(pos)
                else:
                    st.warning("No explicit growth capital terms identified.")
