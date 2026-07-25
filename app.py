import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="InvestWise India - Beginner Hub", page_icon="🟢", layout="wide")

# Custom Styling
st.markdown("""
<style>
    .stApp { background: #080c14; color: #f3f4f6; }
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
    }
    .brand-title { font-size: 1.2rem; font-weight: 700; color: #60a5fa; }
    .brand-desc { font-size: 0.85rem; color: #9ca3af; margin-bottom: 10px; }
    .metric-green { color: #10b981; font-size: 1.5rem; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

st.title("🟢 InvestWise AI: Your Investment Guide")
st.caption("No financial experience needed — explore businesses you already use every day.")

# --- CURATED EVERYDAY BRANDS DATA ---
EVERYDAY_BRANDS = {
    "Zomato / Blinkit": {"ticker": "ZOMATO.NS", "desc": "Food delivery & 10-minute grocery delivery app."},
    "Tata Motors": {"ticker": "TATAMOTORS.NS", "desc": "Makes Nexon, Punch, EV cars, and Jaguar Land Rover."},
    "HDFC Bank": {"ticker": "HDFCBANK.NS", "desc": "India's largest private bank (Credit cards, loans, savings)."},
    "Bharti Airtel": {"ticker": "BHARTIARTL.NS", "desc": "Mobile network, 5G data, and DTH connections."},
    "Asian Paints": {"ticker": "ASIANPAINT.NS", "desc": "Paints 8 out of 10 homes in India."},
    "Titan (Tanishq)": {"ticker": "TITAN.NS", "desc": "Owns Tanishq jewellery, Fastrack, and Titan watches."},
    "Reliance (Jio/Retail)": {"ticker": "RELIANCE.NS", "desc": "Jio telecom, Reliance Fresh, trends, and oil refineries."}
}

SECTORS = {
    "🚗 Cars & Bikes": [
        {"name": "Tata Motors", "ticker": "TATAMOTORS.NS", "desc": "Passenger cars & EVs"},
        {"name": "Maruti Suzuki", "ticker": "MARUTI.NS", "desc": "India's highest selling car maker"},
        {"name": "Mahindra & Mahindra", "ticker": "M&M.NS", "desc": "SUVs (Thar, XUV700) & Tractors"}
    ],
    "🏦 Banks & Finance": [
        {"name": "State Bank of India (SBI)", "ticker": "SBIN.NS", "desc": "Largest government bank in India"},
        {"name": "HDFC Bank", "ticker": "HDFCBANK.NS", "desc": "Largest private sector bank"},
        {"name": "ICICI Bank", "ticker": "ICICIBANK.NS", "desc": "Major private bank & digital banking leader"}
    ],
    "💻 Tech & IT": [
        {"name": "TCS (Tata Consultancy)", "ticker": "TCS.NS", "desc": "Global IT services giant"},
        {"name": "Infosys", "ticker": "INFY.NS", "desc": "Software & tech consulting leader"},
        {"name": "HCLTech", "ticker": "HCLTECH.NS", "desc": "IT engineering & cloud solutions"}
    ]
}

# --- NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs(["🛒 Everyday Brands", "🏭 Explore By Sector", "🏦 Mutual Funds For Beginners"])

# ==========================================
# TAB 1: BRANDS YOU KNOW
# ==========================================
with tab1:
    st.markdown("### 1. Pick a brand you know in real life:")
    st.caption("You don't need to guess ticker symbols — just click on a company you recognize!")
    
    # Grid of Everyday Brand Cards
    cols = st.columns(3)
    selected_ticker = None
    selected_name = None
    
    for idx, (brand_name, info) in enumerate(EVERYDAY_BRANDS.items()):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="glass-card">
                <div class="brand-title">{brand_name}</div>
                <div class="brand-desc">{info['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Analyze {brand_name}", key=f"btn_{idx}"):
                selected_ticker = info['ticker']
                selected_name = brand_name

    # Detailed Analysis view if a button was clicked
    if selected_ticker:
        st.markdown("---")
        st.markdown(f"### 📊 Business Deep Dive: **{selected_name}**")
        
        with st.spinner("Fetching live stock details..."):
            try:
                ticker = yf.Ticker(selected_ticker)
                hist = ticker.history(period="6mo")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[0]
                    pct_return = ((current_price - prev_price) / prev_price) * 100
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f'<div class="glass-card">Current Share Price<br><span class="metric-green">₹{current_price:,.2f}</span></div>', unsafe_allow_html=True)
                    with c2:
                        color = "#10b981" if pct_return >= 0 else "#ef4444"
                        st.markdown(f'<div class="glass-card">6-Month Return<br><span style="color:{color}; font-size:1.5rem; font-weight:800;">{pct_return:+.1f}%</span></div>', unsafe_allow_html=True)
                    
                    # Simple Candlestick Chart
                    hist.reset_index(inplace=True)
                    hist['Date'] = pd.to_datetime(hist['Date']).dt.strftime('%Y-%m-%d')
                    
                    fig = go.Figure(data=[go.Candlestick(
                        x=hist['Date'], open=hist['Open'], high=hist['High'],
                        low=hist['Low'], close=hist['Close'],
                        increasing_line_color='#10b981', decreasing_line_color='#ef4444'
                    )])
                    fig.update_layout(
                        title=f"{selected_name} Price Trend (Past 6 Months)",
                        template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)', height=380, xaxis_rangeslider_visible=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error("Could not fetch data for this brand right now.")

# ==========================================
# TAB 2: EXPLORE BY SECTOR
# ==========================================
with tab2:
    st.markdown("### 2. Choose an Industry to See Its Market Leaders:")
    sector_choice = st.selectbox("Select an Industry:", list(SECTORS.keys()))
    
    st.markdown(f"#### Top Companies in {sector_choice}:")
    for item in SECTORS[sector_choice]:
        st.markdown(f"""
        <div class="glass-card">
            <span style="font-size:1.1rem; font-weight:700; color:#60a5fa;">{item['name']}</span>
            <p style="color:#9ca3af; margin:4px 0 0 0;"><b>What they do:</b> {item['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# TAB 3: MUTUAL FUNDS FOR BEGINNERS
# ==========================================
with tab3:
    st.markdown("### 3. Mutual Funds Explained Simply")
    st.info("💡 **What is a Mutual Fund?** Instead of buying 1 stock yourself, a professional manager collects money from thousands of people and buys a basket of 30–50 stocks for you.")
    
    st.markdown("#### Pick a goal to explore sample top-rated fund types:")
    
    goal = st.radio("What is your primary investment goal?", [
        "🌱 Low Risk (Safety First / Better than Bank FD)",
        "🚀 High Growth (Long Term Wealth - 5+ Years)",
        "⚖️ Balanced (Mix of Equity Stocks & Safe Bonds)"
    ])
    
    if "Low Risk" in goal:
        st.success("Recommended Category: **Liquid & Debt Mutual Funds**\n\n- Low volatility\n- Higher liquidity\n- Ideal for holding emergency savings")
    elif "High Growth" in goal:
        st.warning("Recommended Category: **Flexi Cap / Nifty 50 Index Funds**\n\n- Invests in top 50 companies in India\n- Subject to market ups and downs\n- Historically generates solid returns over 5+ year periods")
    else:
        st.info("Recommended Category: **Aggressive Hybrid Funds**\n\n- ~70% in stocks for growth + 30% in bonds for safety\n- Cushions the drop when markets fall")
