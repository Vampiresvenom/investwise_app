import streamlit as st
import asyncio
from multi_agent_engine import InvestWiseOrchestrator

st.set_page_config(page_title="InvestWise: Multi-Agent Hub", page_icon="🧠", layout="wide")

st.markdown("""
<style>
    .stApp { background: #070a13; color: #f3f4f6; }
    .agent-card {
        background: rgba(255, 255, 255, 0.03);
        border-left: 4px solid;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧠 InvestWise AI: Multi-Agent Orchestrator")
st.caption("Routing complex financial data through specialized LLM agents.")

ticker = st.text_input("Enter Ticker (e.g., TATAMOTORS.NS):", value="TATAMOTORS.NS")

# Simulated live data fetch that would come from your DataEngine
mock_live_data = {
    "price": 980.50,
    "profile": {"pe": 15, "debt_to_equity": 110, "roe": 12},
    "news": ["Freight costs jump 20%", "New EV factory delayed by 3 months"]
}

if st.button("Run Multi-Agent Research", type="primary"):
    with st.spinner("Orchestrating AI Agents..."):
        
        # Initialize the Orchestrator
        orchestrator = InvestWiseOrchestrator()
        
        # Run the async workflow
        results = asyncio.run(orchestrator.run_research_workflow(mock_live_data))
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚙️ Worker Agent Outputs")
            st.markdown(f"""
            <div class="agent-card" style="border-left-color: #3b82f6;">
                <b>🤖 Fundamental Analyst (Fast Model)</b><br>
                <span style="color:#9ca3af;">{results['fundamental_raw']}</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="agent-card" style="border-left-color: #ef4444;">
                <b>🚨 Risk & News Analyst (Fast Model)</b><br>
                <span style="color:#9ca3af;">{results['risk_raw']}</span>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("### 👔 Chief Investment Officer")
            st.markdown(f"""
            <div class="agent-card" style="border-left-color: #10b981; background: rgba(16, 185, 129, 0.05);">
                <b>🧠 Final Synthesis (Heavy Reasoning Model)</b><br>
                <span style="color:#f3f4f6; font-size:1.1rem;">{results['final_verdict']}</span>
            </div>
            """, unsafe_allow_html=True)
