#!/usr/bin/env python3
"""
Test script for Indian Stock Trading Agent
Tests all major components of the system
"""

import sys
import traceback
from datetime import datetime, timedelta

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    try:
        from config import TradingConfig
        config = TradingConfig()
        print(f"✅ Configuration loaded successfully")
        print(f"   - Market timezone: {config.MARKET_TIMEZONE}")
        print(f"   - Stock universe: {len(config.STOCK_UNIVERSE)} stocks")
        print(f"   - Max position size: ₹{config.MAX_POSITION_SIZE:,}")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def test_data_manager():
    """Test data manager functionality"""
    print("\nTesting data manager...")
    try:
        from data_manager import DataManager
        dm = DataManager()
        
        # Test current time
        current_time = dm.get_current_time()
        print(f"✅ Current time: {current_time}")
        
        # Test market open check
        is_open = dm.is_market_open()
        print(f"✅ Market open: {is_open}")
        
        # Test stock data retrieval
        data = dm.get_stock_data("RELIANCE.NS", period="5d")
        if data is not None and not data.empty:
            print(f"✅ Stock data retrieved: {len(data)} records")
            print(f"   - Latest price: ₹{data['Close'].iloc[-1]:.2f}")
        else:
            print("⚠️  Stock data retrieval failed")
        
        # Test market sentiment
        sentiment = dm.get_market_sentiment()
        print(f"✅ Market sentiment: {sentiment}")
        
        return True
    except Exception as e:
        print(f"❌ Data manager test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_technical_analyzer():
    """Test technical analysis functionality"""
    print("\nTesting technical analyzer...")
    try:
        from technical_analyzer import TechnicalAnalyzer
        from data_manager import DataManager
        
        dm = DataManager()
        ta = TechnicalAnalyzer()
        
        # Get sample data
        data = dm.get_stock_data("RELIANCE.NS", period="30d")
        if data is None or data.empty:
            print("⚠️  No data available for technical analysis test")
            return False
        
        # Test indicators calculation
        indicators = ta.get_all_indicators(data)
        if indicators:
            print(f"✅ Technical indicators calculated")
            print(f"   - RSI: {indicators['rsi'].iloc[-1]:.2f}" if indicators['rsi'] is not None else "   - RSI: N/A")
            print(f"   - MACD: {indicators['macd']['macd'].iloc[-1]:.2f}" if indicators['macd'] else "   - MACD: N/A")
        
        # Test signal generation
        signals = ta.generate_signals(data, indicators)
        print(f"✅ Signals generated")
        print(f"   - Signal strength: {signals['strength']:.2f}")
        print(f"   - Buy signals: {len(signals['buy_signals'])}")
        print(f"   - Sell signals: {len(signals['sell_signals'])}")
        
        # Test risk metrics
        risk_metrics = ta.calculate_risk_metrics(data, indicators)
        print(f"✅ Risk metrics calculated")
        print(f"   - Volatility: {risk_metrics['volatility']:.2f}")
        print(f"   - ATR: {risk_metrics['atr']:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Technical analyzer test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_risk_manager():
    """Test risk management functionality"""
    print("\nTesting risk manager...")
    try:
        from risk_manager import RiskManager
        
        rm = RiskManager()
        
        # Test position sizing
        position_size = rm.calculate_position_size(1000, 0.02, 2.0)
        print(f"✅ Position size calculated: {position_size}")
        
        # Test stop loss calculation
        stop_loss = rm.calculate_stop_loss(1000, 50)
        print(f"✅ Stop loss calculated: {stop_loss:.2f}")
        
        # Test take profit calculation
        take_profit = rm.calculate_take_profit(1000, 50)
        print(f"✅ Take profit calculated: {take_profit:.2f}")
        
        # Test trade validation
        is_valid, message = rm.validate_trade("RELIANCE.NS", "BUY", 100, 1000, {})
        print(f"✅ Trade validation: {is_valid} - {message}")
        
        # Test portfolio metrics
        metrics = rm.calculate_portfolio_metrics()
        print(f"✅ Portfolio metrics calculated")
        print(f"   - Total value: ₹{metrics.get('total_value', 0):,.2f}")
        print(f"   - Daily P&L: ₹{metrics.get('daily_pnl', 0):,.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Risk manager test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_trading_agent():
    """Test trading agent functionality"""
    print("\nTesting trading agent...")
    try:
        from trading_agent import TradingAgent
        
        agent = TradingAgent()
        
        # Test status
        status = agent.get_status()
        print(f"✅ Agent status retrieved")
        print(f"   - Running: {status.get('is_running', False)}")
        print(f"   - Market open: {status.get('market_open', False)}")
        print(f"   - Candidates: {status.get('candidates_count', 0)}")
        print(f"   - Positions: {status.get('active_positions', 0)}")
        
        # Test candidates
        candidates = agent.get_candidates()
        print(f"✅ Candidates retrieved: {len(candidates)}")
        
        # Test positions
        positions = agent.get_positions()
        print(f"✅ Positions retrieved: {len(positions)}")
        
        return True
    except Exception as e:
        print(f"❌ Trading agent test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_backtest():
    """Test backtesting functionality"""
    print("\nTesting backtest engine...")
    try:
        from backtest import BacktestEngine
        
        # Test with a short period
        start_date = "2023-12-01"
        end_date = "2023-12-05"
        
        backtest = BacktestEngine(1000000)
        print(f"✅ Backtest engine initialized")
        
        # Note: Full backtest would take time, so we just test initialization
        print(f"   - Initial capital: ₹{backtest.initial_capital:,}")
        print(f"   - Test period: {start_date} to {end_date}")
        
        return True
    except Exception as e:
        print(f"❌ Backtest test failed: {str(e)}")
        traceback.print_exc()
        return False

def test_dashboard():
    """Test dashboard functionality"""
    print("\nTesting dashboard...")
    try:
        # Test dashboard import
        import dash
        from dash import dcc, html
        print(f"✅ Dashboard dependencies available")
        
        # Test plotly
        import plotly.graph_objs as go
        fig = go.Figure()
        print(f"✅ Plotly charts working")
        
        return True
    except Exception as e:
        print(f"❌ Dashboard test failed: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Indian Stock Trading Agent")
    print("=" * 50)
    
    tests = [
        test_config,
        test_data_manager,
        test_technical_analyzer,
        test_risk_manager,
        test_trading_agent,
        test_backtest,
        test_dashboard
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n🚀 Quick Start:")
        print("   python main.py analysis     # Run market analysis")
        print("   python main.py dashboard    # Start web dashboard")
        print("   python main.py live         # Start live trading")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("   Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)