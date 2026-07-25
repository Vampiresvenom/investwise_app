# app.py
import streamlit as st
import plotly.graph_objects as go
from data_engine import DataEngine
from ai_analyzer import BusinessAnalyzer

# 1. Page Configuration
st.set_page_config(page_title="InvestWise AI", page_icon="⚡", layout="wide")

# 2. Dynamic 3D Glassmorphism CSS Styling
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #111827 50%, #070a13 100%);
        color: #f3f4f6;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        margin-bottom: 20px;
    }
    .metric-title {
        color: #9ca3af;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .metric-val {
        font-size: 1.5rem;
        font-weight: 800;
        color: #60a5fa;
        margin-top: 4px;
    }
    .badge-green {
        background: rgba(16, 185, 129, 0.2);
        color: #34d399;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .badge-amber {
        background: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-red {
        background: rgba(239, 68, 68, 0.2);
        color: #f87171;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.title("⚡ InvestWise AI")
st.caption("AI-Powered Investment Research Platform | Institutional Evidence Engine")

# --- SIDEBAR CONTROL PANEL ---
st.sidebar.header("🔍 Research Control Panel")

# Mode Selection
app_mode = st.sidebar.radio("Navigation:", ["Stock & Business Intelligence", "IPO / DRHP Risk Scanner"])

eli5_mode = st.sidebar.toggle("💡 ELI5 Beginner Mode (Plain English)", value=False)

if app_mode == "Stock & Business Intelligence":
    ticker_input = st.sidebar.text_input(
        "Enter Ticker Symbol:",
        value="TATAMOTORS.NS",
        help="Use .NS for Indian stocks (e.g., RELIANCE.NS, INFY.NS) or US symbols (e.g., AAPL, NVDA, MSFT)"
    )
    time_frame = st.sidebar.selectbox("Price Chart Horizon:", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)

    if ticker_input:
        with st.spinner(f"Verifying live tick data for {ticker_input}..."):
            profile = DataEngine.get_stock_profile(ticker_input)
            df_hist = DataEngine.get_historical_with_technicals(ticker_input, period=time_frame)
            news = DataEngine.get_recent_news(ticker_input)

        if "error" in profile:
            st.error(profile["error"])
        else:
            latest_tech = df_hist.iloc[-1].to_dict() if not df_hist.empty else {}
            analysis = BusinessAnalyzer.generate_full_analysis(profile, latest_tech, news)

            # --- TOP METRICS GRID ---
            c1, c2, c3, c4, c5 = st.columns(5)
            
            with c1:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">Live Price</div>
                    <div class="metric-val">{profile['currency']} {profile['current_price']:,}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with c2:
                pe_disp = profile['pe_ratio'] if profile['pe_ratio'] else "N/A"
                st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">P/E Ratio</div>
                    <div class="metric-val">{pe_disp}</div>
                </div>
                """, unsafe_allow_html=True)

            with c3:
                mos = analysis['margin_of_safety']
                badge_class = "badge-green" if mos > 0 else "badge-red"
                st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">Margin of Safety</div>
                    <div class="metric-val"><span class="{badge_class}">{mos}%</span></div>
                </div>
                """, unsafe_allow_html=True)

            with c4:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">RSI (Momentum)</div>
                    <div class="metric-val">{analysis['rsi']}</div>
                </div>
                """, unsafe_allow_html=True)

            with c5:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="metric-title">Altman Z-Score</div>
                    <div class="metric-val" style="color:{analysis['altman_z']['color']};">{analysis['altman_z']['score']}</div>
                </div>
                """, unsafe_allow_html=True)

            # --- MAIN INTERACTIVE DASHBOARD ---
            col_chart, col_thesis = st.columns([1.8, 1.2])

            with col_chart:
                st.markdown(f"### 📈 {profile['name']} - Dynamic Price Action")
                if not df_hist.empty:
                    fig = go.Figure()
                    
                    # Candlesticks
                    fig.add_trace(go.Candlestick(
                        x=df_hist.index,
                        open=df_hist['Open'], high=df_hist['High'],
                        low=df_hist['Low'], close=df_hist['Close'],
                        name="Price",
                        increasing_line_color='#10b981', decreasing_line_color='#ef4444'
                    ))
                    
                    # SMA Overlays
                    fig.add_trace(go.Scatter(x=df_hist.index, y=df_hist['SMA_50'], name="50 SMA", line=dict(color='#f59e0b', width=1.5)))
                    
                    # Bollinger Bands
                    fig.add_trace(go.Scatter(x=df_hist.index, y=df_hist['BB_Upper'], name="Upper Band", line=dict(color='rgba(255,255,255,0.2)', dash='dash')))
                    fig.add_trace(go.Scatter(x=df_hist.index, y=df_hist['BB_Lower'], name="Lower Band", line=dict(color='rgba(255,255,255,0.2)', dash='dash')))

                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        height=420,
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col_thesis:
                st.markdown("### 🤖 Institutional AI Thesis")
                
                if eli5_mode:
                    st.info("💡 **Beginner Mode Active:** Explaining metrics in everyday language.")
                    st.write(f"• **Valuation:** DCF Intrinsic value estimate is **{profile['currency']} {analysis['dcf_valuation']}** per share.")
                    st.write(f"• **Safety Score:** {analysis['altman_z']['zone']}")
                    st.write(f"• **Chart Trend:** {analysis['tech_verdict']}")
                else:
                    st.write(f"• **DCF Fair Value:** {profile['currency']} {analysis['dcf_valuation']}")
                    st.write(f"• **Graham Number:** {profile['currency']} {analysis['graham_number']}")
                    st.write(f"• **Balance Sheet Health:** {analysis['altman_z']['zone']}")
                    st.write(f"• **Technical Setup:** {analysis['tech_verdict']}")

                st.markdown("#### Key Strengths")
                for s in analysis['strengths']:
                    st.markdown(f"- ✅ {s}")

                st.markdown("#### Key Identified Risks")
                for r in analysis['risks']:
                    st.markdown(f"- ⚠️ {r}")

            # --- BUSINESS SUMMARY & NEWS ---
            st.markdown("---")
            st.markdown("### 🏢 Core Business Overview")
            st.write(profile["summary"])

            st.markdown("### 📰 Recent Verified Headlines")
            for item in analysis["recent_news"]:
                st.markdown(f"- **[{item['publisher']}]** [{item['title']}]({item['link']})")

elif app_mode == "IPO / DRHP Risk Scanner":
    st.markdown("### 📄 IPO Draft Prospectus (DRHP) Risk Scanner")
    st.caption("Paste excerpts from 'Objects of the Issue' or 'Risk Factors' section of an upcoming IPO to scan for flags.")

    drhp_text = st.text_area("Paste DRHP Text Segment Here:", height=200, placeholder="Paste text describing how the company plans to use IPO funds or ongoing litigation...")

    if st.button("Scan Prospectus Text", type="primary"):
        if drhp_text:
            drhp_analysis = BusinessAnalyzer.analyze_drhp_text(drhp_text)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### 🚨 Identified Red Flags")
                for flag in drhp_analysis['red_flags']:
                    st.error(flag)
            with col2:
                st.markdown("#### 🟢 Positive Signals")
                for pos in drhp_analysis['positive_signals']:
                    st.success(pos)
        else:
            st.warning("Please paste DRHP text to perform analysis.")
