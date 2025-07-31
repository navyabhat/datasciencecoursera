# 🇮🇳 Indian Stock Trading Agent

A comprehensive, intelligent intraday trading system designed specifically for the Indian stock market. This trading agent combines advanced technical analysis, risk management, and real-time market data to identify and execute profitable trading opportunities.

## 🚀 Features

### 📊 Advanced Technical Analysis
- **Multiple Indicators**: RSI, MACD, Bollinger Bands, Stochastic, ATR, EMA/SMA
- **Volume Analysis**: Volume surge detection, OBV, Volume ROC
- **Momentum Indicators**: Williams %R, CCI, Money Flow Index
- **Trend Analysis**: Multi-timeframe trend detection and strength measurement

### 🛡️ Risk Management
- **Position Sizing**: Dynamic position sizing based on ATR and portfolio risk
- **Stop Loss**: Dynamic stop-loss calculation using ATR
- **Take Profit**: Automated take-profit levels
- **Portfolio Risk**: Maximum drawdown protection and correlation analysis
- **Daily Limits**: Configurable daily loss and trade limits

### 📈 Market Intelligence
- **Real-time Data**: Live market data from multiple sources
- **Market Sentiment**: Nifty 50, Bank Nifty, and VIX analysis
- **Sector Analysis**: Sector-wise performance tracking
- **Volume Surge**: Detection of unusual volume activity
- **Market Breadth**: Advance/decline ratio analysis

### 🎯 Trading Strategy
- **Intraday Focus**: Optimized for Indian market hours (9:15 AM - 3:30 PM)
- **Signal Generation**: Multi-factor signal scoring system
- **Candidate Selection**: Top-ranked trading opportunities
- **Automated Execution**: Real-time trade execution and monitoring

### 📱 Web Dashboard
- **Real-time Monitoring**: Live portfolio and market data
- **Interactive Charts**: Technical analysis visualization
- **Position Tracking**: Active positions and P&L monitoring
- **Market Overview**: Sentiment and sector performance

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd indian-stock-trading-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure the system**
```bash
# Copy and edit configuration if needed
cp config.py config_local.py
# Edit config_local.py with your settings
```

4. **Run the system**
```bash
# Start live trading
python main.py live

# Start web dashboard
python main.py dashboard

# Run market analysis
python main.py analysis

# Run backtesting
python main.py backtest --start-date 2023-01-01 --end-date 2023-12-31
```

## 📋 Configuration

The system is highly configurable through `config.py`:

### Trading Parameters
```python
MAX_POSITION_SIZE = 100000  # Maximum position size in INR
STOP_LOSS_PERCENTAGE = 2.0  # Stop loss percentage
TAKE_PROFIT_PERCENTAGE = 3.0  # Take profit percentage
MAX_DAILY_LOSS = 50000  # Maximum daily loss limit
MAX_DAILY_TRADES = 10  # Maximum trades per day
```

### Technical Analysis
```python
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
```

### Risk Management
```python
MAX_PORTFOLIO_RISK = 0.02  # 2% maximum portfolio risk per trade
CORRELATION_THRESHOLD = 0.7  # Maximum correlation between positions
```

## 🎯 Usage Examples

### Live Trading
```bash
# Start live trading agent
python main.py live

# The agent will:
# - Monitor market during trading hours
# - Scan for trading opportunities
# - Execute trades based on signals
# - Manage risk and positions
```

### Web Dashboard
```bash
# Start web dashboard
python main.py dashboard

# Access dashboard at: http://localhost:8050
# Features:
# - Real-time market data
# - Portfolio monitoring
# - Technical analysis charts
# - Trading candidates
```

### Market Analysis
```bash
# Run market analysis without trading
python main.py analysis

# Output includes:
# - Market sentiment
# - Volume surge stocks
# - Sector performance
# - Market breadth indicators
```

### Backtesting
```bash
# Run backtest on historical data
python main.py backtest --start-date 2023-01-01 --end-date 2023-12-31 --capital 1000000

# Results include:
# - Total return
# - Sharpe ratio
# - Maximum drawdown
# - Trade statistics
```

## 📊 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Manager  │    │ Technical       │    │ Risk Manager    │
│                 │    │ Analyzer        │    │                 │
│ • Real-time     │    │ • RSI, MACD     │    │ • Position      │
│   data          │    │ • Bollinger     │    │   sizing        │
│ • Market        │    │ • Stochastic    │    │ • Stop loss     │
│   sentiment     │    │ • Volume        │    │ • Take profit   │
│ • Volume surge  │    │   analysis      │    │ • Portfolio     │
└─────────────────┘    └─────────────────┘    │   risk          │
         │                       │            └─────────────────┘
         │                       │                     │
         └───────────────────────┼─────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Trading Agent   │
                    │                 │
                    │ • Signal        │
                    │   generation    │
                    │ • Trade         │
                    │   execution     │
                    │ • Position      │
                    │   monitoring    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Web Dashboard   │
                    │                 │
                    │ • Real-time     │
                    │   monitoring    │
                    │ • Charts        │
                    │ • Controls      │
                    └─────────────────┘
```

## 📈 Trading Strategy

### Signal Generation
The system uses a multi-factor approach to generate trading signals:

1. **Technical Indicators**: RSI, MACD, Bollinger Bands, Stochastic
2. **Volume Confirmation**: High volume validation for signals
3. **Trend Analysis**: Multi-timeframe trend strength
4. **Market Sentiment**: Nifty 50 and sector performance
5. **Risk Assessment**: Volatility and correlation analysis

### Position Sizing
- **Risk-based**: Position size calculated using ATR and portfolio risk
- **Maximum limits**: Configurable maximum position and portfolio exposure
- **Correlation check**: Avoid over-concentration in sectors

### Risk Management
- **Dynamic stop-loss**: Based on ATR (2x ATR)
- **Take profit**: Based on ATR (3x ATR)
- **Daily limits**: Maximum daily loss and trade count
- **Portfolio protection**: Maximum drawdown limits

## 🔧 Advanced Configuration

### Custom Stock Universe
Edit `config.py` to modify the stock universe:
```python
STOCK_UNIVERSE = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    # Add your preferred stocks
]
```

### Custom Indicators
Modify `technical_analyzer.py` to add custom indicators:
```python
def calculate_custom_indicator(self, data):
    # Your custom indicator logic
    pass
```

### Risk Parameters
Adjust risk management in `risk_manager.py`:
```python
def calculate_position_size(self, stock_price, risk_per_trade, stop_loss_percentage):
    # Custom position sizing logic
    pass
```

## 📊 Performance Metrics

The system tracks comprehensive performance metrics:

- **Total Return**: Overall portfolio performance
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Ratio of gross profit to gross loss
- **Average Trade**: Average profit/loss per trade

## 🚨 Risk Disclaimer

**IMPORTANT**: This trading system is for educational and research purposes only. Trading stocks involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results.

### Key Risks:
- **Market Risk**: Stock prices can go down as well as up
- **Liquidity Risk**: Some stocks may be difficult to buy or sell
- **System Risk**: Technical failures can affect trading
- **Regulatory Risk**: Changes in regulations can impact trading

### Recommendations:
- Start with paper trading
- Use only risk capital you can afford to lose
- Monitor the system regularly
- Understand the trading strategy before using real money

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the documentation
- Review the code comments

## 🔄 Updates

Stay updated with the latest features:
- Follow the repository for updates
- Check the changelog
- Review configuration changes

---

**Happy Trading! 📈💰**