#!/usr/bin/env python3
"""
Indian Stock Trading Agent - Main Entry Point
A comprehensive intraday trading system for Indian markets
"""

import argparse
import sys
import os
from datetime import datetime
import signal
import time

from trading_agent import TradingAgent
from data_manager import DataManager
from config import TradingConfig
from loguru import logger

def setup_logging():
    """Setup logging configuration"""
    logger.remove()  # Remove default handler
    logger.add(
        "trading_agent.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        level="INFO",
        rotation="1 day",
        retention="7 days"
    )
    logger.add(
        sys.stderr,
        format="{time:HH:mm:ss} | {level} | {message}",
        level="INFO"
    )

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info("Received shutdown signal, stopping trading agent...")
    if hasattr(signal_handler, 'agent'):
        signal_handler.agent.stop()
    sys.exit(0)

def run_backtest(start_date, end_date, initial_capital=1000000):
    """Run backtesting on historical data"""
    logger.info(f"Starting backtest from {start_date} to {end_date}")
    
    try:
        from backtest import BacktestEngine
        backtest = BacktestEngine(initial_capital)
        results = backtest.run(start_date, end_date)
        
        logger.info("Backtest completed successfully")
        logger.info(f"Final Portfolio Value: ₹{results['final_value']:,.2f}")
        logger.info(f"Total Return: {results['total_return']:.2f}%")
        logger.info(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        logger.info(f"Max Drawdown: {results['max_drawdown']:.2f}%")
        
        return results
        
    except Exception as e:
        logger.error(f"Backtest failed: {str(e)}")
        return None

def run_live_trading():
    """Run live trading agent"""
    logger.info("Starting live trading agent...")
    
    try:
        agent = TradingAgent()
        signal_handler.agent = agent  # Store reference for signal handler
        
        # Start the agent
        agent.start()
        
        logger.info("Trading agent started successfully")
        logger.info("Press Ctrl+C to stop the agent")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, stopping agent...")
        agent.stop()
    except Exception as e:
        logger.error(f"Error in live trading: {str(e)}")
        if 'agent' in locals():
            agent.stop()

def run_dashboard():
    """Run the web dashboard"""
    logger.info("Starting web dashboard...")
    
    try:
        from dashboard import app
        app.run_server(debug=False, host='0.0.0.0', port=8050)
        
    except Exception as e:
        logger.error(f"Error starting dashboard: {str(e)}")

def run_analysis():
    """Run market analysis without trading"""
    logger.info("Running market analysis...")
    
    try:
        data_manager = DataManager()
        
        # Get market sentiment
        sentiment = data_manager.get_market_sentiment()
        logger.info(f"Market Sentiment: {sentiment}")
        
        # Get volume surge stocks
        volume_surge = data_manager.get_volume_surge_stocks()
        logger.info(f"Volume Surge Stocks: {len(volume_surge)}")
        for stock in volume_surge[:5]:
            logger.info(f"  {stock['symbol']}: {stock['surge_ratio']:.2f}x volume")
        
        # Get sector performance
        sector_performance = data_manager.get_sector_performance()
        logger.info("Sector Performance:")
        for sector, performance in sector_performance.items():
            logger.info(f"  {sector}: {performance:.2f}%")
        
        # Get market breadth
        breadth = data_manager.get_market_breadth()
        if breadth:
            logger.info(f"Market Breadth: {breadth['advancing']} advancing, {breadth['declining']} declining")
            logger.info(f"Advance/Decline Ratio: {breadth['advance_decline_ratio']:.2f}")
        
    except Exception as e:
        logger.error(f"Error in market analysis: {str(e)}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Indian Stock Trading Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py live                    # Run live trading
  python main.py dashboard               # Run web dashboard
  python main.py analysis                # Run market analysis
  python main.py backtest 2023-01-01 2023-12-31  # Run backtest
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['live', 'dashboard', 'analysis', 'backtest'],
        help='Trading mode to run'
    )
    
    parser.add_argument(
        '--start-date',
        help='Start date for backtest (YYYY-MM-DD)',
        default='2023-01-01'
    )
    
    parser.add_argument(
        '--end-date',
        help='End date for backtest (YYYY-MM-DD)',
        default='2023-12-31'
    )
    
    parser.add_argument(
        '--capital',
        type=float,
        help='Initial capital for backtest (default: 1,000,000)',
        default=1000000
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file',
        default='config.py'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Validate configuration
    if not os.path.exists(args.config):
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("🇮🇳 Indian Stock Trading Agent")
    logger.info("=" * 60)
    logger.info(f"Mode: {args.mode}")
    logger.info(f"Configuration: {args.config}")
    
    # Check market hours
    data_manager = DataManager()
    if data_manager.is_market_open():
        logger.info("✅ Market is currently open")
    else:
        logger.info("❌ Market is currently closed")
    
    try:
        if args.mode == 'live':
            run_live_trading()
        elif args.mode == 'dashboard':
            run_dashboard()
        elif args.mode == 'analysis':
            run_analysis()
        elif args.mode == 'backtest':
            run_backtest(args.start_date, args.end_date, args.capital)
        else:
            logger.error(f"Unknown mode: {args.mode}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()