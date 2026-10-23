# Dashboard User Guide

**No trading experience needed.** This guide explains how to use the backtesting dashboard.

## What You're Looking At

This is an **interactive tool** where you can:
- Test the ensemble trading strategy on the last 10 years of stock market data
- See how it would have performed in the past (backtest)
- See if the strategy is still working recently (forward test)
- Adjust parameters and rerun instantly

Think of it like a **time machine** for trading strategies.

---

## The Dashboard Tabs

### Tab 1: 📊 Performance Metrics (Most Important)

This shows **side-by-side comparison** of how the strategy performed in two time periods.

#### Left Side: "Backtest Period" (70% of data)
This is what the strategy did on past data it "trained" on.

**Key Numbers:**
- **Sharpe Ratio (1.35)**: How much profit per unit of risk. Higher is better.
  - Good: > 1.0
  - Excellent: > 2.0
  - This one: ✅ Good
  
- **Annualized Return (15%)**: If you invested $100, how much annually?
  - Average stock market: 10%
  - This one: ✅ Above average
  
- **Max Drawdown (-12%)**: Worst you lost from peak to bottom
  - Think: "My $1000 would have dropped to $880"
  - Is -12% okay? Yes, typical for active strategies
  - Anything > -50% is high risk
  
- **Calmar Ratio (1.25)**: Return divided by drawdown (higher is better)
  - Tells you if the return is worth the risk

#### Right Side: "Forward Test Period" (30% recent data)
This is how the strategy would do on **newer data** it hasn't seen.

**Why this matters:**
- Backtest can be optimized too much ("overfitting")
- Forward test shows if it's **actually working** now
- If forward test is worse than backtest → Strategy might be broken

**Red flag:** Forward test much worse than backtest

---

### Tab 2: 📈 Equity Curve (Visualize Growth)

This is a **graph of your money over time**.

- **Blue area (left side)**: Backtest period
- **Orange dashed (right side)**: Forward test (recent)

**What to look for:**
- ✅ Generally going up = good
- ❌ Sharp drops = drawdowns (normal)
- ✅ Recover after drops = good risk management

**Bottom stats:**
- **Final Portfolio Value**: Started at $1.00, now at $X.XX
- **Peak Equity**: Highest portfolio value reached
- **Total Return**: Overall profit percentage
- **Risk-Off Days**: Days when system reduced risk (if equity filter is on)

**Example interpretation:**
```
- Started: $1.00
- Peak: $1.50 (50% gain!)
- Current: $1.32 (32% gain)
- = Currently 12% below peak (normal)
```

---

### Tab 3: 📉 Returns Distribution (Advanced)

**Left chart: Daily Returns Histogram**
- Shows frequency of winning vs losing days
- Bell curve = normal (healthy)
- Multiple peaks = inconsistent

**Right chart: Rolling Sharpe (63-day window)**
- How good is the strategy *right now*?
- Spiky = inconsistent performance
- Smooth = reliable

**Bottom stats:**
- **Mean Daily Return**: Average profit per day (e.g., +0.04%)
- **Std Dev**: How "jumpy" returns are
- **Max Daily Gain**: Best single day (normal: +2% to +5%)
- **Worst Daily Loss**: Worst single day (normal: -2% to -5%)

**Healthy pattern:**
```
Mean: +0.04% per day
Std Dev: ±1.5%
Max Gain: +4%
Max Loss: -3%
→ Consistent, not too wild
```

---

## Left Sidebar: Adjust Settings

### Historical Data (years)
Slider: 5 to 15 years

- **5 years**: Quick test, less data
- **10 years** (default): Good balance
- **15 years**: Maximum history, slowest

*First load takes ~30-60 seconds to download data*

### Enable Risk Management
Toggle: ON / OFF

- **ON** (recommended): Strategy reduces risk during bad markets
- **OFF**: Pure strategy, no risk management
- What does it do? If market is falling, sell half, keep 50% in safe index fund

### Backtest/Forward Split
Slider: 50% to 90%

- **70%** (default): 70% past data, 30% recent data
- Higher % = more data for testing, less for validation
- Lower % = more recent data to validate on (good for checking if it's working NOW)

**Recommendation:**
- Use 70% for normal testing
- Use 50% if you want to validate on very recent data

---

## Quick Reference: What Numbers Mean

| Metric | Meaning | Good Value | Red Flag |
|--------|---------|-----------|----------|
| **Sharpe Ratio** | Returns per unit of risk | > 1.0 | < 0.5 |
| **Annualized Return** | Average yearly profit | 10-20% | < 5% |
| **Max Drawdown** | Worst loss | > -20% | < -50% |
| **Calmar Ratio** | Risk-adjusted return | > 0.5 | < 0.1 |
| **Win Rate** | % profitable days | > 50% | < 40% |

---

## Interpreting Results

### Scenario 1: Good Performance
```
Backtest:    Sharpe 1.35, Return 15%, MDD -12%
Forward:     Sharpe 1.10, Return 12%, MDD -10%
→ ✅ GOOD - Forward test still working, slight decay is normal
```

### Scenario 2: Overfitted
```
Backtest:    Sharpe 2.50, Return 50%, MDD -5%
Forward:     Sharpe 0.30, Return 2%, MDD -25%
→ ❌ BAD - Forward test collapsed, strategy was overfitted
```

### Scenario 3: Improving
```
Backtest:    Sharpe 1.00, Return 8%, MDD -15%
Forward:     Sharpe 1.40, Return 14%, MDD -8%
→ ✅ EXCELLENT - Strategy improving, less drawdown recently
```

### Scenario 4: Recent Decline
```
Backtest:    Sharpe 1.35, Return 15%, MDD -12%
Forward:     Sharpe 0.70, Return 5%, MDD -20%
→ ⚠️ CAUTION - Strategy underperforming recently, needs investigation
```

---

## FAQ

**Q: Why does it take 30-60 seconds to load?**
A: Fetching 10 years of stock data. After first load, it's cached for 24 hours.

**Q: Can I trust these numbers?**
A: This is backtested on real historical data, but:
- Past performance ≠ future results
- Real trading has slippage, commissions, taxes
- Market conditions change
- Use this as research tool, not investment advice

**Q: What if forward test is worse?**
A: Small decay is normal (5-20% worse). Large decay suggests overfitting or changing markets.

**Q: Should I trade this strategy?**
A: This is educational tool. Before real trading:
- Do your own research
- Start small (1-2% portfolio)
- Use stop losses
- Consult a financial advisor

**Q: Why 50/50 active/passive?**
A: Combines:
- Active management (top 5 stocks, 50%)
- Passive diversification (broad index, 50%)
- Result: Good returns with lower risk than pure active

**Q: What stocks are in this?**
A: Large-cap US stocks (Apple, Microsoft, Google, etc.)
- Liquid (easy to trade)
- Well-researched
- Lower default risk

**Q: Can I change the stocks?**
A: Yes! Edit the `STOCKS` list in the code if you're technical.
Otherwise, ask the creator.

---

## Disclaimer

⚠️ **This tool is for educational and research purposes only.**

- This is NOT financial advice
- Past performance does NOT guarantee future results
- Actual trading may have different results due to:
  - Commissions and fees
  - Slippage (price movement during execution)
  - Taxes
  - Timing differences
  - Market regime changes
- Always use proper risk management
- Consult a licensed financial advisor before deploying capital
- Your capital is at risk

---

## Need Help?

- **Something confusing?** Read the "About" tab in the dashboard
- **Questions?** Check HOSTING_PLATFORMS.md and DEPLOYMENT_GUIDE.md
- **Found a bug?** Report on GitHub

---

**Happy backtesting! 📈**
