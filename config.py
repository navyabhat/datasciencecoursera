import os
from dotenv import load_dotenv

load_dotenv()

class TradingConfig:
    # Market Settings
    MARKET_TIMEZONE = "Asia/Kolkata"
    MARKET_OPEN_TIME = "09:15"
    MARKET_CLOSE_TIME = "15:30"
    PRE_MARKET_OPEN = "09:00"
    POST_MARKET_CLOSE = "15:45"
    
    # Trading Parameters
    MAX_POSITION_SIZE = 100000  # Maximum position size in INR
    STOP_LOSS_PERCENTAGE = 2.0  # Stop loss percentage
    TAKE_PROFIT_PERCENTAGE = 3.0  # Take profit percentage
    MAX_DAILY_LOSS = 50000  # Maximum daily loss limit in INR
    MAX_DAILY_TRADES = 10  # Maximum number of trades per day
    
    # Technical Analysis Parameters
    RSI_PERIOD = 14
    RSI_OVERBOUGHT = 70
    RSI_OVERSOLD = 30
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BOLLINGER_PERIOD = 20
    BOLLINGER_STD = 2
    
    # Volume Analysis
    MIN_VOLUME_THRESHOLD = 1000000  # Minimum volume for stock selection
    VOLUME_SURGE_THRESHOLD = 2.0  # Volume surge multiplier
    
    # Risk Management
    MAX_PORTFOLIO_RISK = 0.02  # 2% maximum portfolio risk per trade
    CORRELATION_THRESHOLD = 0.7  # Maximum correlation between positions
    
    # Database Settings
    DATABASE_URL = "sqlite:///trading_agent.db"
    
    # API Settings
    NSE_API_BASE_URL = "https://www.nseindia.com"
    YAHOO_FINANCE_BASE_URL = "https://finance.yahoo.com"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "trading_agent.log"
    
    # Notification Settings
    ENABLE_NOTIFICATIONS = True
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Backtesting
    BACKTEST_START_DATE = "2023-01-01"
    BACKTEST_END_DATE = "2024-01-01"
    
    # Stock Universe (Nifty 50 + High Volume Stocks)
    STOCK_UNIVERSE = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
        "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
        "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "HCLTECH.NS", "SUNPHARMA.NS",
        "TATAMOTORS.NS", "WIPRO.NS", "ULTRACEMCO.NS", "TITAN.NS", "BAJFINANCE.NS",
        "NESTLEIND.NS", "POWERGRID.NS", "BAJAJFINSV.NS", "NTPC.NS", "HINDALCO.NS",
        "JSWSTEEL.NS", "ONGC.NS", "TATACONSUM.NS", "BRITANNIA.NS", "COALINDIA.NS",
        "CIPLA.NS", "DIVISLAB.NS", "EICHERMOT.NS", "DRREDDY.NS", "SHREECEM.NS",
        "HEROMOTOCO.NS", "ADANIENT.NS", "TECHM.NS", "TATASTEEL.NS", "BPCL.NS",
        "INDUSINDBK.NS", "GRASIM.NS", "M&M.NS", "LT.NS", "ADANIPORTS.NS",
        "UPL.NS", "TATACONSUM.NS", "APOLLOHOSP.NS", "SBILIFE.NS", "HDFCLIFE.NS"
    ]