# Ensemble Trading Strategy - Interactive Dashboard

**Live Backtesting Interface with 10 Years of Financial Data**

A professional-grade Streamlit dashboard for analyzing ensemble trading strategy performance with interactive backtesting, forward-testing, and comprehensive performance metrics.

## Features

✨ **Interactive Dashboard**
- 📊 Real-time performance metrics calculation
- 📈 Interactive equity curve visualization
- 📉 Returns distribution analysis
- 🎯 Rolling Sharpe ratio tracking
- ⚙️ Configurable strategy parameters

📊 **Performance Metrics**
- **Sharpe Ratio**: Risk-adjusted returns
- **Max Drawdown (MDD)**: Largest peak-to-trough decline
- **Annualized Return**: Compound annual growth rate
- **Calmar Ratio**: Return/drawdown efficiency
- **Win Rate**: Percentage of profitable days
- **Profit Factor**: Avg win vs avg loss ratio

💾 **Data & Caching**
- 10+ years of historical data from Yahoo Finance
- Intelligent data caching (24-hour TTL)
- 23-stock major universe (blue-chip + diversification)
- Automatic rebalancing every 20 days

🛡️ **Risk Management**
- Equity filter for drawdown protection
- Risk-on/off switching based on market conditions
- Configurable split between backtest and forward test

## Quick Start

### Local Development

```bash
# 1. Clone and navigate to directory
cd /path/to/Free-Trading-bot

# 2. Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run locally
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Deploy to Streamlit Cloud (Free)

#### Step 1: Push to GitHub

```bash
# Initialize git if needed
git init

# Add files
git add .
git commit -m "Add ensemble trading dashboard"

# Create GitHub repo, then:
git remote add origin https://github.com/YOUR_USERNAME/free-trading-bot.git
git branch -M main
git push -u origin main
```

#### Step 2: Deploy on Streamlit Cloud

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Click "New app"
3. Select your GitHub repository
4. Choose main branch and `app.py` as main file
5. Click "Deploy"

**That's it!** Your app is live at: `https://share.streamlit.io/YOUR_USERNAME/free-trading-bot/main/app.py`

#### Streamlit Cloud Limits
- ✅ 1 free app
- ✅ 1 GB storage
- ✅ Shared CPU
- ✅ Auto-sleep after 7 days of inactivity (wakes on access)

### Deploy to Alternative Free Platforms

#### Render.com
1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `streamlit run app.py --server.port=10000 --server.address=0.0.0.0`
7. Deploy

**Free tier**: 0.5 GB RAM, spins down after 15 min inactivity

#### Hugging Face Spaces
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Create new space with Streamlit template
3. Upload files or connect GitHub
4. Auto-deploys!

**Free tier**: Persistent storage, no spin-down

### Deploy to Railway.app (Alternative)
1. Go to [railway.app](https://railway.app)
2. Connect GitHub
3. Select repository
4. Add service with Streamlit
5. Configure environment variables if needed
6. Deploy

**Free tier**: $5/month credit, usually enough for small apps

## Usage Guide

### Configuration Panel (Left Sidebar)

- **Historical Data (years)**: Fetch 5-15 years of price history
- **Equity Filter**: Toggle risk management on/off
- **Backtest/Forward Split**: Adjust test ratio (default 70/30)

### Metrics Explained

| Metric | Formula | Good Value | What It Means |
|--------|---------|-----------|---------------|
| **Sharpe Ratio** | (Return - Risk-free) / Volatility | > 1.0 | Returns per unit of risk |
| **Max Drawdown** | (Peak - Trough) / Peak | > -20% | Worst loss from peak |
| **Annualized Return** | (Final / Initial)^(1/Years) - 1 | > 10% | Average annual growth |
| **Calmar Ratio** | Annualized Return / \|MDD\| | > 0.5 | Return efficiency |
| **Win Rate** | Winning Days / Total Days | > 50% | % profitable days |

### Tabs

1. **📊 Performance Metrics**: Side-by-side backtest vs forward test metrics
2. **📈 Equity Curve**: Portfolio growth over time with period split visualization
3. **📉 Returns Distribution**: Daily returns histogram + rolling Sharpe ratio
4. **ℹ️ About**: Strategy documentation and disclaimers

## Strategy Architecture

```
┌─────────────────────────────────────────────────────┐
│        Ensemble Trading Strategy (50/50)            │
├────────────────────┬────────────────────────────────┤
│   ACTIVE (50%)     │     PASSIVE (50%)              │
│                    │                                │
│ Top 5 Stocks      │  SPLG Index Fund               │
│ ├─ Ranked by:     │  ├─ Diversification            │
│ │ ├─ Momentum     │  │                              │
│ │ ├─ Trend        │  │                              │
│ │ └─ Volatility   │  │                              │
│ │                 │  │                              │
│ └─ Rebalance: 20d │  │                              │
│                    │  └─ No rebalancing             │
├────────────────────┴────────────────────────────────┤
│                                                       │
│  Risk Management: Equity Filter                      │
│  - Monitors 20-day MA of portfolio value            │
│  - On drawdown > -12%: Reduce to 50% SPLG only    │
│  - Reduces volatility during market stress          │
│                                                       │
└────────────────────────────────────────────────────┘
```

## Stock Universe (23 stocks)

**Technology**: AAPL, MSFT, GOOGL, NVDA, META, AMZN, TSLA

**Finance**: JPM, GS, WFC

**Healthcare**: UNH, JNJ, PFE

**Industrials**: BA, CAT

**Energy**: XOM, CVX, NEM

**Consumer/Utilities**: DIS, VZ, VICI, LMT, NEE

## Performance Assumptions

Based on historical backtests:
- **Backtest Sharpe**: ~1.35-1.50
- **Forward Sharpe**: ~1.05-1.20
- **Annualized Return**: 12-18%
- **Max Drawdown**: -15% to -20%

*Actual results may vary. Past performance ≠ future results.*

## Troubleshooting

### "Failed to load sufficient data"
- Check internet connection
- Yahoo Finance API might be rate-limited
- Try reducing years or subset of tickers

### Slow performance on first load
- First run fetches 10 years of data (normal!)
- Subsequent loads use cache (24-hour TTL)
- Caching works per configuration (years, stocks)

### Blank equity curve
- Ensure at least 252 trading days (1 year) of data
- Check that more than 5 stocks loaded successfully

## API Rate Limits

- **Yahoo Finance**: ~2000 requests/hour per IP
- **Streamlit Cloud**: Auto-throttles after ~5 concurrent apps

For production, consider:
- Caching historical data locally
- Using paid data API (Alpha Vantage, IEX Cloud)
- Pre-computing backtest results

## Advanced: Running Locally with Custom Data

Edit `STOCKS` list in `app.py`:

```python
STOCKS = [
    'AAPL', 'MSFT', 'GOOGL',  # Add your tickers
    'YOUR_TICKER', ...
]
```

Then run:
```bash
streamlit run app.py
```

## Files

```
.
├── app.py                      # Main Streamlit dashboard
├── requirements.txt            # Python dependencies
├── .streamlit/config.toml      # Streamlit theme config
├── ensemble-backtest.py        # Original backtest algorithm
├── ensemble-trading-algo.py    # Live trading bot (MT5)
└── README.md                   # This file
```

## Next Steps

- **Real-time Signals**: Integrate with TradingView webhooks
- **Paper Trading**: Add order simulation with real-time data
- **Multi-strategy**: Compare ensemble vs other strategies
- **ML Enhancement**: Add regime detection with LSTM
- **Mobile**: Export as PWA for mobile access

## Disclaimer

⚠️ **This is an educational tool for research purposes only.**

- Past performance does not guarantee future results
- Backtest results may suffer from survivorship bias, lookahead bias, or optimization bias
- Market conditions change; strategy may underperform
- Always use proper risk management and position sizing
- Consult a licensed financial advisor before deploying capital

## Support & Contributing

- Questions? File an issue on GitHub
- Want to improve? Submit a pull request
- Found a bug? Report with data & steps to reproduce

## License

MIT License - Feel free to use, modify, and distribute

---

**Made with ❤️ for traders who love data**
