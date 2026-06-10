import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
import base64
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Multi-Stock Trading Dashboard", layout="wide", page_icon="📊")

# Initialize session state for multiple stock portfolios
if 'portfolios' not in st.session_state:
    st.session_state.portfolios = {}

# Stock list with their details
ticker_options = {
    "SBIN.NS": {"name": "State Bank of India", "sector": "Banking", "icon": "🏦"},
    "RELIANCE.NS": {"name": "Reliance Industries", "sector": "Energy", "icon": "🛢️"},
    "TCS.NS": {"name": "Tata Consultancy Services", "sector": "IT", "icon": "💻"},
    "INFY.NS": {"name": "Infosys", "sector": "IT", "icon": "💻"},
    "HDFCBANK.NS": {"name": "HDFC Bank", "sector": "Banking", "icon": "🏦"},
    "ICICIBANK.NS": {"name": "ICICI Bank", "sector": "Banking", "icon": "🏦"},
    "ITC.NS": {"name": "ITC Limited", "sector": "FMCG", "icon": "🚬"},
    "WIPRO.NS": {"name": "Wipro", "sector": "IT", "icon": "💻"},
    "AXISBANK.NS": {"name": "Axis Bank", "sector": "Banking", "icon": "🏦"},
    "KOTAKBANK.NS": {"name": "Kotak Mahindra Bank", "sector": "Banking", "icon": "🏦"}
}

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .signal-card {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin: 10px 0;
        transition: transform 0.3s;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .buy-signal {
        background: linear-gradient(135deg, #00c853 0%, #00e676 100%);
        border-left: 5px solid #00ff00;
        box-shadow: 0 0 20px rgba(0,200,0,0.3);
    }
    
    .sell-signal {
        background: linear-gradient(135deg, #d50000 0%, #ff1744 100%);
        border-left: 5px solid #ff0000;
        box-shadow: 0 0 20px rgba(255,0,0,0.3);
    }
    
    .hold-signal {
        background: linear-gradient(135deg, #ff9800 0%, #ffc107 100%);
        border-left: 5px solid #ffaa00;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        transition: transform 0.3s;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: #667eea;
    }
    
    .profit-card {
        background: linear-gradient(135deg, #00c85320 0%, #00e67620 100%);
        border-left: 4px solid #00c853;
        animation: glow-green 1s ease-in-out infinite alternate;
    }
    
    .loss-card {
        background: linear-gradient(135deg, #d5000020 0%, #ff174420 100%);
        border-left: 4px solid #d50000;
        animation: glow-red 1s ease-in-out infinite alternate;
    }
    
    @keyframes glow-green {
        from { box-shadow: 0 0 5px #00c85320; }
        to { box-shadow: 0 0 15px #00c853; }
    }
    
    @keyframes glow-red {
        from { box-shadow: 0 0 5px #d5000020; }
        to { box-shadow: 0 0 15px #d50000; }
    }
    
    .transaction-card {
        background: #1e1e1e;
        padding: 12px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 3px solid;
        transition: all 0.3s;
    }
    
    .transaction-card:hover {
        transform: translateX(5px);
    }
    
    .buy-transaction {
        border-left-color: #00c853;
        background: linear-gradient(90deg, #00c85310 0%, #1e1e1e 100%);
    }
    
    .sell-transaction {
        border-left-color: #d50000;
        background: linear-gradient(90deg, #d5000010 0%, #1e1e1e 100%);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        font-weight: bold;
        border-radius: 25px;
        transition: all 0.3s;
        width: 100%;
        font-size: 16px;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .price-up {
        color: #00c853;
        font-weight: bold;
        animation: blink 1s infinite;
    }
    
    .price-down {
        color: #d50000;
        font-weight: bold;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .live-badge {
        background-color: #ff4444;
        color: white;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
        animation: blink 1s infinite;
    }
    
    .stock-selector {
        background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown(f"""
<div class="main-header">
    <h1 style="color: white; text-align: center; margin: 0;">📊 Multi-Stock Trading Dashboard</h1>
    <p style="color: white; text-align: center; margin: 10px 0 0 0;">AI-Powered Trading | Separate Portfolio for Each Stock | Real-time P&L</p>
    <p style="color: white; text-align: center; margin: 5px 0 0 0; font-size: 12px;">🟢 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} <span class="live-badge">LIVE</span></p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🎛️ Dashboard Controls")
    
    # Stock selection
    selected_stock = st.selectbox(
        "📈 Select Stock",
        options=list(ticker_options.keys()),
        format_func=lambda x: f"{ticker_options[x]['icon']} {ticker_options[x]['name']} ({x})"
    )
    
    stock_name = ticker_options[selected_stock]['name']
    stock_icon = ticker_options[selected_stock]['icon']
    stock_sector = ticker_options[selected_stock]['sector']
    
    st.markdown(f"""
    <div class="stock-selector">
        <h3>{stock_icon} {stock_name}</h3>
        <p>Sector: {stock_sector}</p>
        <p>Symbol: {selected_stock}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize portfolio for selected stock if not exists
    if selected_stock not in st.session_state.portfolios:
        st.session_state.portfolios[selected_stock] = {
            'holdings': [],
            'cash': 100000.0,
            'total_invested': 0.0,
            'current_value': 0.0,
            'transactions': [],
            'total_pnl': 0.0,
            'total_pnl_percent': 0.0
        }
    
    # Get current portfolio
    portfolio = st.session_state.portfolios[selected_stock]
    
    st.markdown("---")
    st.markdown("## ⚙️ Settings")
    forecast_days = st.slider("📅 Forecast Days", 7, 30, 15)
    risk_level = st.selectbox("⚠️ Risk Level", ["Low", "Medium", "High"], index=1)
    epochs = st.slider("🤖 Training Epochs", 3, 20, 5)
    show_technical = st.checkbox("📊 Show Technical Indicators", value=True)
    
    st.markdown("---")
    st.markdown(f"## 💼 {stock_icon} {stock_name} Portfolio")
    total_value = portfolio['cash'] + portfolio['current_value']
    pnl = total_value - 100000
    pnl_pct = (pnl / 100000) * 100
    st.markdown(f"**Cash:** ₹{portfolio['cash']:,.2f}")
    st.markdown(f"**Holdings:** ₹{portfolio['current_value']:,.2f}")
    st.markdown(f"**Total:** ₹{total_value:,.2f}")
    st.markdown(f"**P&L:** {'+' if pnl >= 0 else ''}₹{pnl:,.2f} ({pnl_pct:+.1f}%)")

# Load data for selected stock
@st.cache_data(ttl=60)
def load_data(ticker):
    with st.spinner(f"📥 Fetching {ticker_options[ticker]['name']} data..."):
        data = yf.download(ticker, start="2015-01-01", progress=False)
        return data.dropna()

data = load_data(selected_stock)

if data.empty:
    st.error(f"❌ No data found for {stock_name}")
    st.stop()

# Calculate indicators for selected stock
def calculate_indicators(data):
    df = data.copy()
    close_prices = df['Close'].squeeze()
    
    df['SMA_20'] = close_prices.rolling(window=20).mean()
    df['SMA_50'] = close_prices.rolling(window=50).mean()
    df['EMA_12'] = close_prices.ewm(span=12, adjust=False).mean()
    df['EMA_26'] = close_prices.ewm(span=26, adjust=False).mean()
    
    delta = close_prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    bb_middle = close_prices.rolling(window=20).mean()
    bb_std = close_prices.rolling(window=20).std()
    if isinstance(bb_middle, pd.DataFrame):
        bb_middle = bb_middle.iloc[:, 0]
    if isinstance(bb_std, pd.DataFrame):
        bb_std = bb_std.iloc[:, 0]
    
    df['BB_Upper'] = bb_middle + (bb_std * 2)
    df['BB_Lower'] = bb_middle - (bb_std * 2)
    
    return df

data = calculate_indicators(data)

# Get live price for selected stock
try:
    info = yf.Ticker(selected_stock).info
    current_price = info.get('currentPrice', info.get('regularMarketPrice', float(data['Close'].iloc[-1])))
    current_price = float(current_price) if current_price else float(data['Close'].iloc[-1])
    previous_close = float(info.get('previousClose', data['Close'].iloc[-2]))
    price_change = current_price - previous_close
    price_change_percent = (price_change / previous_close) * 100
    day_low = float(info.get('dayLow', data['Low'].iloc[-1]))
    day_high = float(info.get('dayHigh', data['High'].iloc[-1]))
    volume = info.get('volume', 0)
except:
    current_price = float(data['Close'].iloc[-1])
    previous_close = float(data['Close'].iloc[-2])
    price_change = current_price - previous_close
    price_change_percent = (price_change / previous_close) * 100
    day_low = float(data['Low'].iloc[-1])
    day_high = float(data['High'].iloc[-1])
    volume = 0

# Update portfolio current value for selected stock
if portfolio['holdings']:
    portfolio['current_value'] = sum([
        h['shares'] * current_price for h in portfolio['holdings']
    ])

# ============ PORTFOLIO SECTION ============
st.markdown(f"## 💼 {stock_icon} {stock_name} - LIVE PORTFOLIO")

col1, col2, col3, col4 = st.columns(4)

total_value = portfolio['cash'] + portfolio['current_value']
initial_capital = 100000
total_pnl = total_value - initial_capital
total_pnl_pct = (total_pnl / initial_capital) * 100

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h4>💰 Cash Balance</h4>
        <h2 style="color: #00c853">₹{portfolio['cash']:,.2f}</h2>
        <small>Available for trading</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h4>📊 Holdings Value</h4>
        <h2 style="color: #667eea">₹{portfolio['current_value']:,.2f}</h2>
        <small>{len(portfolio['holdings'])} shares</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h4>💎 Total Portfolio</h4>
        <h2 style="color: #ff9800">₹{total_value:,.2f}</h2>
        <small>Cash + Holdings</small>
    </div>
    """, unsafe_allow_html=True)

with col4:
    pnl_class = "profit-card" if total_pnl >= 0 else "loss-card"
    st.markdown(f"""
    <div class="metric-card {pnl_class}">
        <h4>📈 Total P&L</h4>
        <h2 style="color: {'#00c853' if total_pnl >= 0 else '#d50000'}">₹{total_pnl:+,.2f}</h2>
        <small>({total_pnl_pct:+.2f}%)</small>
    </div>
    """, unsafe_allow_html=True)

# ============ CURRENT HOLDINGS ============
if portfolio['holdings']:
    st.markdown(f"## 📋 {stock_icon} {stock_name} - CURRENT HOLDINGS")
    
    holdings_data = []
    total_invested = 0
    total_current = 0
    
    for holding in portfolio['holdings']:
        invested = holding['shares'] * holding['buy_price']
        current = holding['shares'] * current_price
        pnl = current - invested
        pnl_pct = (pnl / invested) * 100 if invested > 0 else 0
        
        total_invested += invested
        total_current += current
        
        holdings_data.append({
            'Stock': holding['symbol'],
            'Shares': holding['shares'],
            'Buy Price': f"₹{holding['buy_price']:.2f}",
            'Buy Date': holding['buy_date'],
            'Current Price': f"₹{current_price:.2f}",
            'Invested': f"₹{invested:,.2f}",
            'Current Value': f"₹{current:,.2f}",
            'P&L': f"₹{pnl:+,.2f} ({pnl_pct:+.1f}%)"
        })
    
    st.dataframe(pd.DataFrame(holdings_data), use_container_width=True)
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Invested", f"₹{total_invested:,.2f}")
    with col2:
        st.metric("Current Value", f"₹{total_current:,.2f}")
    with col3:
        unrealized_pnl = total_current - total_invested
        st.metric("Unrealized P&L", f"₹{unrealized_pnl:+,.2f}", 
                 delta=f"{((unrealized_pnl)/total_invested*100):+.1f}%" if total_invested > 0 else "0%")

# ============ TRANSACTION HISTORY ============
if portfolio['transactions']:
    st.markdown(f"## 📜 {stock_icon} {stock_name} - TRANSACTION HISTORY")
    
    for tx in reversed(portfolio['transactions'][-20:]):
        tx_class = "buy-transaction" if tx['type'] == 'BUY' else "sell-transaction"
        profit_text = ""
        if tx['type'] == 'SELL' and 'profit' in tx:
            profit_class = "profit-text" if tx['profit'] >= 0 else "loss-text"
            profit_text = f" | <span class='{profit_class}'>P&L: ₹{tx['profit']:+,.2f}</span>"
        
        st.markdown(f"""
        <div class="transaction-card {tx_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="font-size: 16px;">{tx['type']}</strong> {tx['shares']} shares of <strong>{tx['symbol']}</strong>
                    <br>
                    <small>📅 {tx['date']}</small>
                </div>
                <div style="text-align: right;">
                    <strong>₹{tx['price']:.2f}</strong> per share
                    <br>
                    <strong>Total: ₹{tx['amount']:,.2f}</strong>
                    {profit_text}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============ MARKET OVERVIEW ============
st.markdown(f"## 💹 {stock_icon} {stock_name} - MARKET OVERVIEW")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    price_color = "price-up" if price_change > 0 else "price-down"
    st.markdown(f"""
    <div class="metric-card">
        <h4>💰 Current Price</h4>
        <h2 style="color: {'#00c853' if price_change > 0 else '#d50000'}">₹{current_price:.2f}</h2>
        <p class="{price_color}">{'+' if price_change > 0 else ''}{price_change:.2f} ({price_change_percent:+.2f}%)</p>
        <small>Updated: {datetime.now().strftime('%H:%M:%S')}</small>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h4>📊 Day Range</h4>
        <h3>₹{day_low:.2f} - ₹{day_high:.2f}</h3>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h4>📈 52 Week Range</h4>
        <h3>₹{float(data['Low'].min()):.2f} - ₹{float(data['High'].max()):.2f}</h3>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h4>📊 Volume</h4>
        <h3>{volume:,}</h3>
    </div>
    """, unsafe_allow_html=True)

with col5:
    rsi_value = float(data['RSI'].iloc[-1]) if not pd.isna(data['RSI'].iloc[-1]) else 50
    rsi_color = '#00c853' if rsi_value < 70 else '#ff9800' if rsi_value > 30 else '#d50000'
    st.markdown(f"""
    <div class="metric-card">
        <h4>🎯 RSI (14)</h4>
        <h3 style="color: {rsi_color}">{rsi_value:.1f}</h3>
        <small>{'Overbought' if rsi_value > 70 else 'Oversold' if rsi_value < 30 else 'Neutral'}</small>
    </div>
    """, unsafe_allow_html=True)

# ============ AI MODEL TRAINING ============
scaler = MinMaxScaler()
close_values = data[["Close"]].values
scaled_close = scaler.fit_transform(close_values)

seq_len = 60
X, y = [], []
for i in range(seq_len, len(scaled_close)):
    X.append(scaled_close[i-seq_len:i])
    y.append(scaled_close[i])

X = np.array(X).reshape(-1, seq_len, 1)
y = np.array(y)

if len(X) > 0:
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    from sklearn.linear_model import Ridge
    with st.spinner(f"🤖 Training AI Model for {stock_name}..."):
        X_train_2d = X_train.reshape(X_train.shape[0], -1)
        X_test_2d = X_test.reshape(X_test.shape[0], -1)
        model = Ridge(alpha=1.0)
        model.fit(X_train_2d, y_train.ravel())
    
    last_seq = scaled_close[-seq_len:].copy()
    future_scaled = []
    for _ in range(forecast_days):
        pred = model.predict(last_seq.reshape(1, -1))[0]
        future_scaled.append(pred)
        last_seq = np.append(last_seq[1:], [[pred]], axis=0)
    
    future_prices = scaler.inverse_transform(np.array(future_scaled).reshape(-1, 1)).flatten()
    future_dates = [data.index[-1] + timedelta(days=i+1) for i in range(forecast_days)]
else:
    st.error("❌ Insufficient data")
    st.stop()

# ============ AI SIGNAL GENERATION ============
def generate_signals(current_price, future_prices, rsi, macd, price_change_percent):
    confidence = 0
    reasoning = []
    
    expected_return = ((future_prices[-1] - current_price) / current_price) * 100
    
    if expected_return > 5:
        confidence += 30
        reasoning.append(f"📈 Expected return of {expected_return:.1f}%")
    elif expected_return > 0:
        confidence += 15
        reasoning.append(f"📊 Moderate growth of {expected_return:.1f}%")
    elif expected_return > -5:
        confidence -= 15
        reasoning.append(f"📉 Minor decline of {expected_return:.1f}%")
    else:
        confidence -= 30
        reasoning.append(f"⚠️ Expected decline of {expected_return:.1f}%")
    
    if rsi < 30:
        confidence += 25
        reasoning.append(f"🟢 RSI oversold at {rsi:.1f} (Buying opportunity)")
    elif rsi > 70:
        confidence -= 25
        reasoning.append(f"🔴 RSI overbought at {rsi:.1f} (Selling opportunity)")
    
    if macd > 0:
        confidence += 20
        reasoning.append(f"📊 MACD bullish crossover")
    else:
        confidence -= 20
        reasoning.append(f"📊 MACD bearish signal")
    
    if price_change_percent > 2:
        confidence += 15
        reasoning.append(f"⚡ Strong momentum: +{price_change_percent:.1f}%")
    elif price_change_percent < -2:
        confidence -= 15
        reasoning.append(f"⚡ Weak momentum: {price_change_percent:.1f}%")
    
    if confidence >= 70:
        signal_type = "STRONG BUY"
    elif confidence >= 40:
        signal_type = "BUY"
    elif confidence <= -70:
        signal_type = "STRONG SELL"
    elif confidence <= -40:
        signal_type = "SELL"
    else:
        signal_type = "HOLD"
    
    return signal_type, confidence, reasoning

current_rsi = float(data['RSI'].iloc[-1]) if not pd.isna(data['RSI'].iloc[-1]) else 50
current_macd = float(data['MACD'].iloc[-1]) if not pd.isna(data['MACD'].iloc[-1]) else 0

signal_type, confidence, reasoning = generate_signals(
    current_price, future_prices, current_rsi, current_macd, price_change_percent
)

# ============ TRADING SIGNAL DISPLAY ============
st.markdown(f"## 🎯 {stock_icon} {stock_name} - AI TRADING SIGNAL")
signal_color = "buy-signal" if "BUY" in signal_type else "sell-signal" if "SELL" in signal_type else "hold-signal"

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown(f"""
    <div class="signal-card {signal_color}">
        <h2 style="color: white; font-size: 32px; margin: 0;">{signal_type}</h2>
        <p style="color: white; margin: 10px 0 0 0;">Confidence: {abs(confidence):.0f}% | Risk: {risk_level}</p>
        <p style="color: white; margin: 5px 0 0 0; font-size: 14px;">Generated at: {datetime.now().strftime('%H:%M:%S')}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    expected_return = ((future_prices[-1] - current_price) / current_price) * 100
    st.markdown(f"""
    <div class="metric-card">
        <h4>🎯 Expected Return</h4>
        <h2 style="color: {'#00c853' if expected_return > 0 else '#d50000'}">{expected_return:+.1f}%</h2>
        <small>Next {forecast_days} days</small>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h4>📊 Signal Strength</h4>
        <h1 style="color: {'#00c853' if confidence > 0 else '#d50000'}">{'+' if confidence > 0 else ''}{confidence:.0f}</h1>
        <progress value="{abs(confidence)}" max="100" style="width: 100%; height: 8px; border-radius: 4px;"></progress>
    </div>
    """, unsafe_allow_html=True)

# ============ TRADING ACTION BUTTONS ============
st.markdown("---")
st.markdown(f"## 🎮 EXECUTE TRADE - {stock_name}")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🟢 BUY")
    buy_shares = st.number_input(
        f"Number of shares to buy",
        min_value=1,
        max_value=int(portfolio['cash'] / current_price) if current_price > 0 else 0,
        value=min(10, int(portfolio['cash'] / current_price) if current_price > 0 else 0),
        step=1,
        key=f"buy_{selected_stock}"
    )
    
    buy_total = buy_shares * current_price
    st.markdown(f"**Total Amount:** ₹{buy_total:,.2f}")
    
    if st.button(f"🟢 BUY {buy_shares} shares", use_container_width=True, key=f"buy_btn_{selected_stock}"):
        if buy_shares > 0:
            if portfolio['cash'] >= buy_total:
                cost = buy_total
                portfolio['cash'] -= cost
                portfolio['holdings'].append({
                    'symbol': selected_stock,
                    'shares': buy_shares,
                    'buy_price': current_price,
                    'buy_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                portfolio['total_invested'] += cost
                portfolio['transactions'].append({
                    'type': 'BUY',
                    'symbol': selected_stock,
                    'price': current_price,
                    'shares': buy_shares,
                    'amount': cost,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                portfolio['current_value'] = sum([h['shares'] * current_price for h in portfolio['holdings']])
                
                st.success(f"""
                ✅ **BUY ORDER EXECUTED FOR {stock_name}!**
                
                📊 **Details:**
                - Stock: {stock_name} ({selected_stock})
                - Shares: {buy_shares}
                - Price: ₹{current_price:.2f}
                - Total: ₹{cost:,.2f}
                - Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                """)
                st.balloons()
                st.rerun()
            else:
                st.error(f"❌ Insufficient cash! Need ₹{buy_total:,.2f}, have ₹{portfolio['cash']:,.2f}")
        else:
            st.warning("⚠️ Please enter number of shares to buy")

with col2:
    st.markdown("### 🔴 SELL")
    total_holdings = sum([h['shares'] for h in portfolio['holdings']])
    
    if total_holdings > 0:
        sell_shares = st.number_input(
            f"Number of shares to sell (Max: {total_holdings})",
            min_value=1,
            max_value=total_holdings,
            value=min(10, total_holdings),
            step=1,
            key=f"sell_{selected_stock}"
        )
        
        sell_total = sell_shares * current_price
        st.markdown(f"**Total Amount:** ₹{sell_total:,.2f}")
        
        # Calculate P&L for selected shares (FIFO method)
        remaining_to_sell = sell_shares
        total_cost = 0
        temp_holdings = portfolio['holdings'].copy()
        for holding in temp_holdings:
            if remaining_to_sell <= 0:
                break
            sell_from_this = min(holding['shares'], remaining_to_sell)
            total_cost += sell_from_this * holding['buy_price']
            remaining_to_sell -= sell_from_this
        
        if remaining_to_sell == 0:
            estimated_profit = sell_total - total_cost
            estimated_profit_pct = (estimated_profit / total_cost) * 100 if total_cost > 0 else 0
            st.markdown(f"**Est. P&L:** {'🟢' if estimated_profit >= 0 else '🔴'} ₹{estimated_profit:+,.2f} ({estimated_profit_pct:+.1f}%)")
        
        if st.button(f"🔴 SELL {sell_shares} shares", use_container_width=True, key=f"sell_btn_{selected_stock}"):
            if sell_shares > 0 and sell_shares <= total_holdings:
                # Sell logic with FIFO
                remaining_to_sell = sell_shares
                total_sale_value = 0
                total_cost_basis = 0
                new_holdings = []
                
                for holding in portfolio['holdings']:
                    if remaining_to_sell <= 0:
                        new_holdings.append(holding)
                        continue
                    
                    if holding['shares'] <= remaining_to_sell:
                        # Sell all shares from this holding
                        total_sale_value += holding['shares'] * current_price
                        total_cost_basis += holding['shares'] * holding['buy_price']
                        remaining_to_sell -= holding['shares']
                        # Don't add this holding to new_holdings (sold completely)
                    else:
                        # Sell partial shares from this holding
                        total_sale_value += remaining_to_sell * current_price
                        total_cost_basis += remaining_to_sell * holding['buy_price']
                        # Add remaining shares to new holdings
                        holding['shares'] -= remaining_to_sell
                        new_holdings.append(holding)
                        remaining_to_sell = 0
                
                # Calculate profit
                profit = total_sale_value - total_cost_basis
                profit_pct = (profit / total_cost_basis) * 100 if total_cost_basis > 0 else 0
                
                # Update portfolio
                portfolio['cash'] += total_sale_value
                portfolio['holdings'] = new_holdings
                portfolio['total_invested'] = sum([h['shares'] * h['buy_price'] for h in portfolio['holdings']])
                portfolio['current_value'] = sum([h['shares'] * current_price for h in portfolio['holdings']])
                
                portfolio['transactions'].append({
                    'type': 'SELL',
                    'symbol': selected_stock,
                    'price': current_price,
                    'shares': sell_shares,
                    'amount': total_sale_value,
                    'profit': profit,
                    'profit_pct': profit_pct,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                if profit > 0:
                    st.success(f"""
                    ✅ **SELL ORDER EXECUTED FOR {stock_name}!**
                    
                    📊 **Details:**
                    - Stock: {stock_name} ({selected_stock})
                    - Shares: {sell_shares}
                    - Price: ₹{current_price:.2f}
                    - Total Received: ₹{total_sale_value:,.2f}
                    - Cost Basis: ₹{total_cost_basis:,.2f}
                    - PROFIT: ₹{profit:+,.2f} ({profit_pct:+.1f}%)
                    - Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """)
                    st.balloons()
                else:
                    st.warning(f"""
                    ⚠️ **SELL ORDER EXECUTED FOR {stock_name}**
                    
                    📊 **Details:**
                    - Stock: {stock_name} ({selected_stock})
                    - Shares: {sell_shares}
                    - Price: ₹{current_price:.2f}
                    - Total Received: ₹{total_sale_value:,.2f}
                    - Cost Basis: ₹{total_cost_basis:,.2f}
                    - LOSS: ₹{profit:+,.2f} ({profit_pct:+.1f}%)
                    - Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """)
                st.rerun()
            else:
                st.error(f"❌ Invalid number of shares! You have {total_holdings} shares.")
    else:
        st.markdown("**No holdings to sell**")
        st.number_input("Number of shares to sell", min_value=0, max_value=0, value=0, disabled=True, key=f"sell_disabled_{selected_stock}")
        st.button("🔴 SELL", use_container_width=True, disabled=True)

with col3:
    st.markdown("### 🟡 HOLD")
    st.markdown(f"""
    <div class="metric-card">
        <h4>Current Position</h4>
        <h3>{total_holdings} shares</h3>
        <p>Value: ₹{portfolio['current_value']:,.2f}</p>
        <small>Waiting for better opportunity</small>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(f"🟡 HOLD POSITION", use_container_width=True, key=f"hold_{selected_stock}"):
        st.info(f"""
        ℹ️ **HOLD POSITION MAINTAINED FOR {stock_name}**
        
        Current Position: {total_holdings} shares
        Current Value: ₹{portfolio['current_value']:,.2f}
        Waiting for better opportunity...
        """)
# ============ PORTFOLIO ACTIONS ============
col1, col2 = st.columns(2)

with col1:
    if st.button(f"🔄 RESET {stock_name} PORTFOLIO", use_container_width=True):
        st.session_state.portfolios[selected_stock] = {
            'holdings': [],
            'cash': 100000.0,
            'total_invested': 0.0,
            'current_value': 0.0,
            'transactions': [],
            'total_pnl': 0.0,
            'total_pnl_percent': 0.0
        }
        st.success(f"✅ {stock_name} portfolio reset to ₹1,00,000")
        st.rerun()

with col2:
    if st.button(f"📊 EXPORT {stock_name} TRANSACTIONS", use_container_width=True):
        if portfolio['transactions']:
            tx_df = pd.DataFrame(portfolio['transactions'])
            csv_tx = tx_df.to_csv(index=False)
            b64_tx = base64.b64encode(csv_tx.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64_tx}" download="{selected_stock}_transactions_{datetime.now().strftime("%Y%m%d_%H%M")}.csv" class="download-btn">📥 Download CSV</a>'
            st.markdown(href, unsafe_allow_html=True)

# ============ SIGNAL REASONING ============
with st.expander(f"📝 AI SIGNAL REASONING - {stock_name}", expanded=True):
    for reason in reasoning:
        st.write(f"• {reason}")

# ============ PRICE CHART ============
st.markdown(f"## 📈 {stock_name} - PRICE CHART")

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])

fig.add_trace(go.Candlestick(
    x=data.index[-100:],
    open=data['Open'].iloc[-100:],
    high=data['High'].iloc[-100:],
    low=data['Low'].iloc[-100:],
    close=data['Close'].iloc[-100:],
    name='Price'
), row=1, col=1)

if show_technical:
    fig.add_trace(go.Scatter(x=data.index[-100:], y=data['BB_Upper'].iloc[-100:], 
                            name='BB Upper', line=dict(color='rgba(255,100,100,0.5)', dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index[-100:], y=data['BB_Lower'].iloc[-100:], 
                            name='BB Lower', line=dict(color='rgba(100,255,100,0.5)', dash='dash'), fill='tonexty'), row=1, col=1)

fig.add_trace(go.Scatter(x=data.index[-100:], y=data['RSI'].iloc[-100:], name='RSI', line=dict(color='orange')), row=2, col=1)
fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

fig.update_layout(title=f"{stock_name} - Price Chart", template="plotly_dark", height=600)
st.plotly_chart(fig, use_container_width=True)

# ============ FORECAST SECTION ============
st.markdown(f"## 🔮 NEXT {forecast_days} DAYS FORECAST - {stock_name}")

forecast_data = []
for i in range(len(future_dates)):
    if i == 0:
        change_pct = 0
        signal = "Current"
    else:
        change_pct = ((future_prices[i] - future_prices[i-1]) / future_prices[i-1]) * 100
        if change_pct > 2:
            signal = "🟢 STRONG BUY"
        elif change_pct > 0.5:
            signal = "🟢 BUY"
        elif change_pct < -2:
            signal = "🔴 STRONG SELL"
        elif change_pct < -0.5:
            signal = "🔴 SELL"
        else:
            signal = "🟡 HOLD"
    
    forecast_data.append({
        "Date": future_dates[i].strftime('%Y-%m-%d'),
        "Price": f"₹{future_prices[i]:.2f}",
        "Change": f"{change_pct:+.2f}%",
        "Signal": signal
    })

forecast_df = pd.DataFrame(forecast_data)
st.dataframe(forecast_df, use_container_width=True)

# Forecast Chart
fig_future = go.Figure()
fig_future.add_trace(go.Scatter(x=future_dates, y=future_prices, mode='lines+markers', 
                                name='Forecast', line=dict(color='#667eea', width=3)))

for i in range(len(forecast_df)):
    if 'BUY' in forecast_df.iloc[i]['Signal']:
        fig_future.add_trace(go.Scatter(x=[future_dates[i]], y=[future_prices[i]], mode='markers',
                                       name='Buy' if i==0 else None, marker=dict(symbol='triangle-up', size=15, color='#00c853')))
    elif 'SELL' in forecast_df.iloc[i]['Signal']:
        fig_future.add_trace(go.Scatter(x=[future_dates[i]], y=[future_prices[i]], mode='markers',
                                       name='Sell' if i==0 else None, marker=dict(symbol='triangle-down', size=15, color='#d50000')))

fig_future.update_layout(title=f"{stock_name} - Price Forecast with Signals", xaxis_title="Date", 
                        yaxis_title="Price (₹)", template="plotly_dark", height=500)
st.plotly_chart(fig_future, use_container_width=True)

# ============ DOWNLOAD REPORT ============
st.markdown("## 💾 DOWNLOAD REPORT")

csv_data = forecast_df.to_csv(index=False)
b64_csv = base64.b64encode(csv_data.encode()).decode()
csv_href = f'<a href="data:file/csv;base64,{b64_csv}" download="{selected_stock}_forecast_{datetime.now().strftime("%Y%m%d")}.csv" class="download-btn">📊 Download Forecast CSV</a>'
st.markdown(csv_href, unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;">
    <p style="color: white; margin: 0;">⚠️ Paper Trading Mode | Each Stock has Separate Portfolio</p>
    <p style="color: white; margin: 5px 0 0 0;">🚀 AI-Powered by BiLSTM Neural Network | Real-time P&L Tracking</p>
    <p style="color: white; margin: 5px 0 0 0;">💰 Starting Capital: ₹1,00,000 per stock | Track each stock separately</p>
</div>
""", unsafe_allow_html=True)