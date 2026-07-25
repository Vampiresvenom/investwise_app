import streamlit as st
import yfinance as yf
from forensic_engine import ForensicAIAgent

# 1. Page Configuration
st.set_page_config(page_title="InvestWise AI Forensics", page_icon="🕵️‍♂️", layout="wide")

# Custom Glassmorphism Theme
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
    .macro-card { border-left: 4px solid #3b82f6; padding-left: 15px; margin-bottom: 15px; background: rgba(255,255,255,0.02); padding: 15px; border-radius: 8px;}
</style>
""", unsafe_allow_html=True)

st.title("🕵️‍♂️ InvestWise AI: Forensic Analyst")
st.caption("Going beyond the numbers: Concall Audits, Fine Print Scanning, and Macro Ripple Effects.")

# --- SIDEBAR INPUT ---
st.sidebar.header("Target Company")
ticker_input = st.sidebar.text_input("Enter NSE Stock Symbol:", value="TATAMOTORS")
symbol = ticker_input.upper().strip()
if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
    symbol += ".NS"

st.markdown("---")

if ticker_input:
    with st.spinner(f"Initiating Forensic Scan for {symbol}..."):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            company_name = info.get("shortName", symbol)
            sector = info.get("sector", "Unknown Sector")
            current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)
            
            st.markdown(f"### 🎯 Target: **{company_name}** | Sector: {sector} | Price: ₹{current_price:,.2f}")
            
            # --- THE 3 INTELLIGENCE MOATS ---
            tab1, tab2, tab3 = st.tabs([
                "🗣️ Management Credibility Tracker", 
                "🔎 Notes to Accounts Scanner", 
                "🌍 Macro & Supply Chain Ripple"
            ])
            
            # MOAT 1: Concall Audit
            with tab1:
                st.markdown("### Earnings Call: Promise vs. Reality Audit")
                st.info("The AI cross-checks what the CEO promised 6 months ago against today's actual balance sheet.")
                
                audit = ForensicAIAgent.analyze_management_credibility(symbol)
                
                st.markdown(f"""
                <div class="glass-card">
                    <h4 style="color:{audit['color']}; margin-top:0;">Credibility Rating: {audit['rating']}</h4>
                    <hr style="border-color: rgba(255,255,255,0.1);">
                    <p><b>🗣️ Past Management Promise:</b> {audit['past_promise']}</p>
                    <p><b>📊 Current Balance Sheet Reality:</b> {audit['current_reality']}</p>
                    <div style="background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; margin-top: 15px;">
                        <b>🤖 AI Forensic Verdict:</b> {audit['ai_verdict']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # MOAT 2: Fine Print Scanner
            with tab2:
                st.markdown("### Annual Report: 'Notes to Accounts' Scanner")
                st.caption("Standard screeners ignore the 300-page fine print. The AI extracts hidden red flags from the auditor's notes.")
                
                flags = ForensicAIAgent.scan_notes_to_accounts(symbol)
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                for flag in flags:
                    st.markdown(f"- {flag}")
                st.markdown('</div>', unsafe_allow_html=True)

            # MOAT 3: Supply Chain Ripple
            with tab3:
                st.markdown("### Macroeconomic Ripple Engine")
                st.caption(f"How global events are currently disrupting the **{sector}** supply chain.")
                
                macro_events = ForensicAIAgent.get_macro_ripple_effects(sector)
                
                for event in macro_events:
                    st.markdown(f"""
                    <div class="macro-card" style="border-left-color: {event['color']};">
                        <h4 style="margin: 0 0 5px 0;">{event['event']} <span style="font-size:0.8rem; background:{event['color']}40; padding:2px 8px; border-radius:12px; color:{event['color']}; float:right;">{event['impact']}</span></h4>
                        <p style="margin:0; color:#9ca3af;">{event['detail']}</p>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error accessing corporate data: {str(e)}")
