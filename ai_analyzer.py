# ai_analyzer.py

class BusinessAnalyzer:
    """Institutional Analytics & Quantitative Valuation Engine"""

    @staticmethod
    def calculate_dcf_intrinsic_value(fcf: float, shares_outstanding: float, growth_rate: float = 0.10, discount_rate: float = 0.11, terminal_multiple: float = 12.0) -> float:
        """Calculates Discounted Cash Flow (DCF) intrinsic value per share."""
        if fcf <= 0 or shares_outstanding <= 0:
            return 0.0
            
        future_cash_flows = []
        current_fcf = fcf
        
        # 5-Year Cash Flow Projection
        for year in range(1, 6):
            current_fcf *= (1 + growth_rate)
            discounted_cf = current_fcf / ((1 + discount_rate) ** year)
            future_cash_flows.append(discounted_cf)
            
        # Terminal Value Calculation
        terminal_value = (current_fcf * terminal_multiple) / ((1 + discount_rate) ** 5)
        total_enterprise_value = sum(future_cash_flows) + terminal_value
        
        intrinsic_value_per_share = total_enterprise_value / shares_outstanding
        return round(intrinsic_value_per_share, 2)

    @staticmethod
    def calculate_graham_number(eps: float, book_value: float) -> float:
        """Calculates Benjamin Graham's Intrinsic Value formula: sqrt(22.5 * EPS * BVPS)."""
        if eps is None or book_value is None or eps <= 0 or book_value <= 0:
            return 0.0
        return round((22.5 * eps * book_value) ** 0.5, 2)

    @staticmethod
    def compute_altman_z_score(profile: dict) -> dict:
        """Estimates Altman Z-Score for financial distress and balance sheet safety."""
        current_ratio = profile.get("current_ratio") or 1.2
        debt_to_equity = profile.get("debt_to_equity") or 50.0
        profit_margin = profile.get("profit_margin") or 0.10
        
        # Approximate score based on working capital, leverage, and profitability
        score = 1.5
        if current_ratio > 1.5: score += 0.8
        if debt_to_equity < 80: score += 1.0
        if profit_margin > 0.12: score += 0.9
        
        if score >= 3.0:
            zone = "Safe Zone (Low Default Risk)"
            color = "#10b981"
        elif score >= 1.8:
            zone = "Grey Zone (Moderate Caution)"
            color = "#f59e0b"
        else:
            zone = "Distress Zone (High Balance Sheet Risk)"
            color = "#ef4444"
            
        return {"score": round(score, 2), "zone": zone, "color": color}

    @staticmethod
    def generate_full_analysis(profile: dict, latest_tech: dict, news: list) -> dict:
        """Synthesizes technical, fundamental, valuation, and macroeconomic factors."""
        
        current_price = profile.get("current_price", 0.0)
        eps = profile.get("eps", 0.0)
        book_value = profile.get("book_value", 0.0)
        market_cap = profile.get("market_cap", 0)
        fcf = profile.get("free_cash_flow", 0)
        
        # 1. Valuations
        graham = BusinessAnalyzer.calculate_graham_number(eps, book_value)
        
        shares_out = market_cap / current_price if current_price > 0 else 0
        dcf_val = BusinessAnalyzer.calculate_dcf_intrinsic_value(fcf, shares_out)
        
        # Margin of Safety
        margin_of_safety = 0.0
        ref_val = dcf_val if dcf_val > 0 else graham
        if ref_val > 0 and current_price > 0:
            margin_of_safety = round(((ref_val - current_price) / ref_val) * 100, 1)

        # 2. Balance Sheet Health
        altman = BusinessAnalyzer.compute_altman_z_score(profile)

        # 3. Technical Signals
        rsi = latest_tech.get("RSI", 50.0)
        macd = latest_tech.get("MACD", 0.0)
        macd_signal = latest_tech.get("MACD_Signal", 0.0)
        sma_50 = latest_tech.get("SMA_50", current_price)
        sma_200 = latest_tech.get("SMA_200", current_price)

        tech_verdict = "Neutral Momentum"
        if rsi < 35:
            tech_verdict = "Oversold (Potential Bounce Opportunity)"
        elif rsi > 70:
            tech_verdict = "Overbought (Exercise Caution)"
        elif macd > macd_signal and current_price > sma_50:
            tech_verdict = "Bullish Momentum Trend"

        # 4. Strengths & Risks
        strengths = []
        risks = []

        roe = (profile.get("roe") or 0) * 100
        margin = (profile.get("profit_margin") or 0) * 100
        debt = profile.get("debt_to_equity")

        if roe >= 15:
            strengths.append(f"Strong Return on Equity ({roe:.1f}%): Efficient use of shareholder funds.")
        else:
            risks.append(f"Low Return on Equity ({roe:.1f}%): Below the 15% institutional benchmark.")

        if margin >= 12:
            strengths.append(f"Healthy Net Operating Margin ({margin:.1f}%): Strong market pricing power.")
        else:
            risks.append(f"Thin Net Margin ({margin:.1f}%): Susceptible to inflation and supply chain cost spikes.")

        if debt is not None:
            if debt < 75:
                strengths.append(f"Low Debt Profile (Debt/Equity: {debt:.1f}): Resilient balance sheet.")
            else:
                risks.append(f"High Leverage (Debt/Equity: {debt:.1f}): Higher interest coverage pressure.")

        if margin_of_safety > 15:
            strengths.append(f"Positive Margin of Safety (~{margin_of_safety}%): Trading below calculated intrinsic value.")
        elif margin_of_safety < -20:
            risks.append(f"Valuation Premium (~{abs(margin_of_safety)}% above fair value): Limited margin of safety.")

        return {
            "dcf_valuation": dcf_val,
            "graham_number": graham,
            "margin_of_safety": margin_of_safety,
            "altman_z": altman,
            "tech_verdict": tech_verdict,
            "rsi": round(rsi, 1),
            "strengths": strengths if strengths else ["Business model in stabilization phase."],
            "risks": risks if risks else ["No immediate severe structural flags detected."],
            "recent_news": news
        }

    @staticmethod
    def analyze_drhp_text(drhp_text: str) -> dict:
        """Scans raw text from IPO Draft Red Herring Prospectus (DRHP) for structural red flags."""
        text_lower = drhp_text.lower()
        red_flags = []
        positive_signals = []

        # Keywords scanning
        if "repay debt" in text_lower or "repayment of loan" in text_lower:
            red_flags.append("IPO Funds Used for Debt Repayment: Money is going to lenders rather than business expansion.")
        if "working capital" in text_lower:
            positive_signals.append("Objects of Issue: Funds allocated toward operational working capital.")
        if "litigation" in text_lower or "legal proceedings" in text_lower:
            red_flags.append("Outstanding Legal Proceedings: Unresolved court cases or regulatory inquiries disclosed.")
        if "promoter selling" in text_lower or "offer for sale" in text_lower:
            red_flags.append("Offer for Sale (OFS): Existing promoters/investors cashing out shareholdings.")
        if "capacity expansion" in text_lower or "new factory" in text_lower:
            positive_signals.append("Growth Capital: Proceeds targeted directly at scaling infrastructure.")

        return {
            "red_flags": red_flags if red_flags else ["No automated DRHP red flags detected in provided text segment."],
            "positive_signals": positive_signals if positive_signals else ["No explicit capital expansion terms identified."]
        }
