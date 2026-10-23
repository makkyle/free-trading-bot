"""
ENSEMBLE STRATEGY - Interactive Backtesting Dashboard
Streamlit app for visualizing strategy performance with 10 years of financial data
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging

# Page config
st.set_page_config(
    page_title="Ensemble Trading Strategy Backtest",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== CONFIG ====================
STOCKS = [
    'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META',
    'AMZN', 'TSLA', 'JPM', 'GS', 'WFC',
    'UNH', 'JNJ', 'PFE', 'BA', 'CAT',
    'XOM', 'CVX', 'NEM', 'DIS', 'VZ',
    'VICI', 'LMT', 'NEE'
]

EQUITY_FILTER_MA_WINDOW = 20
EQUITY_FILTER_MIN_HISTORY = 20
EQUITY_FILTER_MAX_DRAWDOWN = -0.12
REBALANCE_DAYS = 20

# ==================== CACHE & FUNCTIONS ====================

@st.cache_data(ttl=86400)
def fetch_price_data(tickers, years=10):
    """Fetch price data from Yahoo Finance with caching"""
    st.info(f"📥 Fetching {len(tickers)} stocks ({years} years of data)...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)
    
    prices_dict = {}
    dates = None
    
    for ticker in tickers:
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if len(data) > 0:
                prices_dict[ticker] = data['Close'].values.astype(float)
                if dates is None:
                    dates = data.index.to_numpy()
        except Exception as e:
            logger.warning(f"Failed to fetch {ticker}: {e}")
    
    return prices_dict, pd.DatetimeIndex(dates)

@st.cache_data(ttl=86400)
def fetch_splg_data(years=10):
    """Fetch SPLG (SPY equivalent) data"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * years)
    
    try:
        data = yf.download('SPLG', start=start_date, end=end_date, progress=False)
        if data is None or len(data) == 0:
            raise ValueError("No SPLG data returned")
        return data['Close'].values.astype(float), data.index.to_numpy()
    except Exception as e:
        logger.warning(f"Failed to fetch SPLG data: {e}. Using SPY as fallback.")
        try:
            data = yf.download('SPY', start=start_date, end=end_date, progress=False)
            if data is None or len(data) == 0:
                raise ValueError("No SPY data returned")
            return data['Close'].values.astype(float), data.index.to_numpy()
        except Exception as e2:
            logger.error(f"Failed to fetch SPY data too: {e2}")
            return np.array([]), np.array([])

def get_factor_score(prices):
    """Score based on momentum, mean reversion, trend"""
    if len(prices) < 60:
        return 0
    
    returns = np.diff(prices) / prices[:-1]
    
    # Momentum (recent returns)
    momentum = np.mean(returns[-20:])
    
    # Trend (MA cross)
    ma20 = np.mean(prices[-20:])
    ma60 = np.mean(prices[-60:])
    trend = 1 if ma20 > ma60 else -1
    
    # Volatility (inverse - prefer stability)
    volatility = np.std(returns[-20:])
    vol_score = -volatility if volatility > 0 else 0
    
    score = momentum * 0.5 + trend * 0.3 + vol_score * 0.2
    return score

def calculate_metrics(returns):
    """Calculate key performance metrics"""
    if len(returns) < 2:
        return {
            'sharpe': 0, 'annualized_return': 0, 'mdd': 0, 'calmar': 0,
            'total_return': 0, 'win_rate': 0, 'avg_win': 0, 'avg_loss': 0
        }
    
    returns_arr = np.array(returns)
    
    # Sharpe Ratio
    mean_return = np.mean(returns_arr)
    std_return = np.std(returns_arr)
    sharpe = (mean_return / (std_return + 1e-8)) * np.sqrt(252)
    
    # Annualized Return
    cumulative = np.cumprod(1 + returns_arr)
    total_return = cumulative[-1] - 1
    years = len(returns_arr) / 252
    annualized_return = (cumulative[-1] ** (1 / years) - 1) if years > 0 else 0
    
    # Max Drawdown
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    mdd = np.min(drawdown)
    
    # Calmar Ratio
    calmar = annualized_return / abs(mdd) if mdd != 0 else 0
    
    # Win Rate & Avg Win/Loss
    winning = returns_arr[returns_arr > 0]
    losing = returns_arr[returns_arr < 0]
    
    win_rate = len(winning) / len(returns_arr) if len(returns_arr) > 0 else 0
    avg_win = np.mean(winning) if len(winning) > 0 else 0
    avg_loss = np.mean(losing) if len(losing) > 0 else 0
    
    return {
        'sharpe': sharpe,
        'annualized_return': annualized_return,
        'mdd': mdd,
        'calmar': calmar,
        'total_return': total_return,
        'win_rate': win_rate,
        'avg_win': avg_win,
        'avg_loss': avg_loss,
    }

def run_backtest(prices_dict, splg_prices, dates, use_equity_filter=True, split_ratio=0.7):
    """Run ensemble backtest"""
    
    tickers = list(prices_dict.keys())
    n_days = len(dates)
    
    # Handle empty SPLG data
    if len(splg_prices) == 0:
        logger.warning("SPLG data is empty, using fallback index data")
        splg_prices = np.ones(n_days)
    
    # Align SPLG to prices length
    if len(splg_prices) > n_days:
        splg_prices = splg_prices[-n_days:]
    elif len(splg_prices) < n_days:
        if len(splg_prices) > 0:
            padding = np.full(n_days - len(splg_prices), splg_prices[0], dtype=float)
            splg_prices = np.concatenate([padding, splg_prices])
        else:
            splg_prices = np.ones(n_days)
    
    cumulative_ensemble = 1.0
    equity_curve = [1.0]
    ensemble_returns_list = []
    blocked_days = 0
    current_top_5 = []
    last_rebalance = 0
    
    for day in range(1, n_days):
        # Rebalance every REBALANCE_DAYS
        if day - last_rebalance >= REBALANCE_DAYS or day < 252:
            if day >= 252:
                scores = {}
                for ticker in tickers:
                    scores[ticker] = get_factor_score(prices_dict[ticker][:day])
                
                top_5_list = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
                current_top_5 = [t[0] for t in top_5_list]
                last_rebalance = day
        
        # Calculate returns
        if len(current_top_5) == 5:
            active_ret = 0.0
            for ticker in current_top_5:
                if day < len(prices_dict[ticker]):
                    ret = (prices_dict[ticker][day] - prices_dict[ticker][day-1]) / prices_dict[ticker][day-1]
                    active_ret += float(ret) / 5.0
            
            splg_ret = float((splg_prices[day] - splg_prices[day-1]) / splg_prices[day-1])
            ensemble_ret = float(0.5 * active_ret + 0.5 * splg_ret)
            
            # Equity filter (risk management)
            if use_equity_filter:
                current_equity = equity_curve[-1]
                lookback = equity_curve[-EQUITY_FILTER_MA_WINDOW:]
                equity_ma = float(np.mean(lookback))
                peak = float(np.max(equity_curve))
                drawdown = (current_equity - peak) / peak if peak > 0 else 0.0
                warmup = len(equity_curve) < EQUITY_FILTER_MIN_HISTORY
                risk_on = warmup or (current_equity >= equity_ma and drawdown >= EQUITY_FILTER_MAX_DRAWDOWN)
                
                if not risk_on:
                    ensemble_ret = splg_ret
                    blocked_days += 1
            
            cumulative_ensemble *= (1.0 + ensemble_ret)
            equity_curve.append(cumulative_ensemble)
            ensemble_returns_list.append(ensemble_ret)
    
    # Split into backtest and forward test
    ensemble_returns = np.array(ensemble_returns_list)
    split_idx = int(len(ensemble_returns) * split_ratio)
    
    bt_returns = ensemble_returns[:split_idx]
    fw_returns = ensemble_returns[split_idx:]
    
    bt_metrics = calculate_metrics(bt_returns)
    fw_metrics = calculate_metrics(fw_returns)
    
    return {
        'equity_curve': equity_curve,
        'returns': ensemble_returns_list,
        'backtest_metrics': bt_metrics,
        'forward_metrics': fw_metrics,
        'dates': dates,
        'blocked_days': blocked_days,
        'split_idx': split_idx,
    }

# ==================== STREAMLIT UI ====================

st.title("📈 Ensemble Trading Strategy Dashboard")
st.markdown("**Interactive backtest with 10 years of historical data**")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    years = st.slider(
        "Historical Data (years)",
        min_value=5, max_value=15, value=10, step=1
    )
    
    equity_filter = st.checkbox(
        "Enable Risk Management (Equity Filter)",
        value=True,
        help="Reduces exposure during drawdown periods"
    )
    
    split_ratio = st.slider(
        "Backtest/Forward Split",
        min_value=0.5, max_value=0.9, value=0.7, step=0.05,
        help="Percentage of data used for backtest"
    )
    
    st.markdown("---")
    st.markdown("**Strategy Details:**")
    st.markdown("""
    - **Universe**: 23 major stocks
    - **Active Portfolio**: Top 5 ranked stocks (50% weight)
    - **Passive Portfolio**: SPLG index (50% weight)
    - **Rebalancing**: Every 20 days
    - **Scoring**: Momentum + Trend + Volatility
    """)

# Main content
st.markdown("---")

# Load data
with st.spinner("Loading market data..."):
    prices_dict, dates = fetch_price_data(STOCKS, years=years)
    splg_prices, splg_dates = fetch_splg_data(years=years)
    
    if len(prices_dict) < 5:
        st.error("❌ Failed to load sufficient data. Please try again.")
        st.stop()
    
    if len(splg_prices) == 0:
        st.warning("⚠️ SPLG index data unavailable. Using fallback index for passive portfolio.")

st.success(f"✅ Loaded {len(prices_dict)} stocks with {len(dates)} trading days")

# Run backtest
with st.spinner("Running backtest..."):
    results = run_backtest(prices_dict, splg_prices, dates, 
                          use_equity_filter=equity_filter, 
                          split_ratio=split_ratio)

# Display metrics in tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Metrics", "📈 Equity Curve", "📉 Returns Distribution", "ℹ️ About"])

# Tab 1: Metrics
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📚 Backtest Period")
        
        bt_m = results['backtest_metrics']
        
        metric_cols = st.columns(2)
        with metric_cols[0]:
            st.metric(
                "Sharpe Ratio",
                f"{bt_m['sharpe']:.2f}",
                help="Risk-adjusted returns (higher is better)"
            )
            st.metric(
                "Annualized Return",
                f"{bt_m['annualized_return']*100:.1f}%"
            )
        
        with metric_cols[1]:
            st.metric(
                "Max Drawdown",
                f"{bt_m['mdd']*100:.1f}%",
                help="Largest peak-to-trough decline"
            )
            st.metric(
                "Calmar Ratio",
                f"{bt_m['calmar']:.2f}",
                help="Annualized return / Max drawdown"
            )
        
        with st.expander("More Backtest Metrics"):
            st.metric("Total Return", f"{bt_m['total_return']*100:.1f}%")
            st.metric("Win Rate", f"{bt_m['win_rate']*100:.1f}%")
            st.metric("Avg Win", f"{bt_m['avg_win']*100:.2f}%")
            st.metric("Avg Loss", f"{bt_m['avg_loss']*100:.2f}%")
    
    with col2:
        st.subheader("🚀 Forward Test Period")
        
        fw_m = results['forward_metrics']
        
        metric_cols = st.columns(2)
        with metric_cols[0]:
            st.metric(
                "Sharpe Ratio",
                f"{fw_m['sharpe']:.2f}",
                help="Risk-adjusted returns (higher is better)"
            )
            st.metric(
                "Annualized Return",
                f"{fw_m['annualized_return']*100:.1f}%"
            )
        
        with metric_cols[1]:
            st.metric(
                "Max Drawdown",
                f"{fw_m['mdd']*100:.1f}%",
                help="Largest peak-to-trough decline"
            )
            st.metric(
                "Calmar Ratio",
                f"{fw_m['calmar']:.2f}",
                help="Annualized return / Max drawdown"
            )
        
        with st.expander("More Forward Test Metrics"):
            st.metric("Total Return", f"{fw_m['total_return']*100:.1f}%")
            st.metric("Win Rate", f"{fw_m['win_rate']*100:.1f}%")
            st.metric("Avg Win", f"{fw_m['avg_win']*100:.2f}%")
            st.metric("Avg Loss", f"{fw_m['avg_loss']*100:.2f}%")

# Tab 2: Equity Curve
with tab2:
    # Create equity curve chart
    equity_df = pd.DataFrame({
        'Date': results['dates'],
        'Equity': results['equity_curve']
    })
    
    fig = go.Figure()
    
    # Backtest period
    bt_end_idx = results['split_idx'] + 1
    
    fig.add_trace(go.Scatter(
        x=equity_df['Date'][:bt_end_idx],
        y=equity_df['Equity'][:bt_end_idx],
        mode='lines',
        name='Backtest',
        line=dict(color='#1f77b4', width=2),
        fill='tozeroy',
        fillcolor='rgba(31, 119, 180, 0.2)'
    ))
    
    fig.add_trace(go.Scatter(
        x=equity_df['Date'][bt_end_idx-1:],
        y=equity_df['Equity'][bt_end_idx-1:],
        mode='lines',
        name='Forward Test',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        fill='tozeroy',
        fillcolor='rgba(255, 127, 14, 0.2)'
    ))
    
    fig.update_layout(
        title='Strategy Equity Curve',
        xaxis_title='Date',
        yaxis_title='Portfolio Value ($)',
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    final_equity = results['equity_curve'][-1]
    initial_equity = results['equity_curve'][0]
    total_pnl = (final_equity - initial_equity) * 100
    
    with col1:
        st.metric("Final Portfolio Value", f"${final_equity:.2f}", f"+${total_pnl:.2f}")
    with col2:
        st.metric("Peak Equity", f"${max(results['equity_curve']):.2f}")
    with col3:
        st.metric("Total Return", f"{((final_equity - 1) * 100):.1f}%")
    with col4:
        if equity_filter:
            st.metric("Risk-Off Days", f"{results['blocked_days']}")

# Tab 3: Returns Distribution
with tab3:
    returns_arr = np.array(results['returns']) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=returns_arr,
            nbinsx=50,
            name='Daily Returns',
            marker_color='#1f77b4'
        ))
        fig_hist.update_layout(
            title='Daily Returns Distribution',
            xaxis_title='Daily Return (%)',
            yaxis_title='Frequency',
            height=400,
            template='plotly_white'
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Rolling Sharpe
        rolling_window = 63  # ~quarterly
        rolling_sharpe = []
        rolling_dates = []
        
        for i in range(rolling_window, len(returns_arr)):
            window_returns = returns_arr[i-rolling_window:i] / 100
            mean_ret = np.mean(window_returns)
            std_ret = np.std(window_returns)
            sharpe = (mean_ret / (std_ret + 1e-8)) * np.sqrt(252)
            rolling_sharpe.append(sharpe)
            rolling_dates.append(results['dates'][i])
        
        fig_roll = go.Figure()
        fig_roll.add_trace(go.Scatter(
            x=rolling_dates,
            y=rolling_sharpe,
            mode='lines',
            name='Rolling Sharpe (63d)',
            line=dict(color='#2ca02c', width=2),
            fill='tozeroy'
        ))
        fig_roll.update_layout(
            title='Rolling Sharpe Ratio (63-day window)',
            xaxis_title='Date',
            yaxis_title='Sharpe Ratio',
            height=400,
            template='plotly_white',
            hovermode='x unified'
        )
        st.plotly_chart(fig_roll, use_container_width=True)
    
    # Statistics
    st.markdown("**Returns Statistics:**")
    stat_cols = st.columns(4)
    
    with stat_cols[0]:
        st.metric("Mean Daily Return", f"{np.mean(returns_arr):.3f}%")
    with stat_cols[1]:
        st.metric("Std Dev (Volatility)", f"{np.std(returns_arr):.3f}%")
    with stat_cols[2]:
        st.metric("Max Daily Gain", f"{np.max(returns_arr):.2f}%")
    with stat_cols[3]:
        st.metric("Worst Daily Loss", f"{np.min(returns_arr):.2f}%")

# Tab 4: About
with tab4:
    st.markdown("""
    ### Strategy Overview
    
    This ensemble strategy combines:
    - **Active Component (50%)**: Top 5 stocks ranked by momentum, trend, and stability
    - **Passive Component (50%)**: SPLG index fund for diversification
    
    ### Key Features
    
    ✅ **Dynamic Rebalancing**: Portfolio rebalances every 20 trading days
    
    ✅ **Risk Management**: Equity filter reduces active exposure during drawdown periods
    
    ✅ **Factor-Based Ranking**: Stocks scored on:
    - Momentum (recent performance)
    - Trend (MA cross-over)
    - Volatility (stability preference)
    
    ✅ **Backtested**: 10 years of historical data
    
    ### Performance Metrics Explained
    
    **Sharpe Ratio**: Risk-adjusted return per unit of volatility (>1.0 is good, >2.0 is excellent)
    
    **Max Drawdown (MDD)**: Largest peak-to-trough loss (-10% is typical for equity strategies)
    
    **Annualized Return**: Compound annual growth rate (CAGR)
    
    **Calmar Ratio**: Annualized return divided by max drawdown (higher is better)
    
    ### Disclaimer
    
    ⚠️ **Past performance does not guarantee future results.** This is a quantitative analysis tool 
    for educational and research purposes. Always conduct thorough due diligence and risk management 
    before deploying capital. Consult with a financial advisor for personalized advice.
    
    ### Data Sources
    
    - Stock prices: Yahoo Finance (OHLCV data)
    - Updates: Daily during market hours
    - History: Up to 15 years available
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.9em;'>
    Built with ❤️ using Streamlit | Last updated: 2024
</div>
""", unsafe_allow_html=True)
