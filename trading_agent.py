import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import schedule
from loguru import logger
import json
import threading

from config import TradingConfig
from data_manager import DataManager
from technical_analyzer import TechnicalAnalyzer
from risk_manager import RiskManager

class TradingAgent:
    def __init__(self):
        self.config = TradingConfig()
        self.data_manager = DataManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.risk_manager = RiskManager()
        
        # Trading state
        self.is_running = False
        self.trading_thread = None
        self.candidates = []
        self.active_positions = {}
        
        # Setup logging
        logger.add(self.config.LOG_FILE, level=self.config.LOG_LEVEL)
        
    def start(self):
        """Start the trading agent"""
        try:
            logger.info("Starting Trading Agent...")
            self.is_running = True
            
            # Schedule market open/close tasks
            schedule.every().day.at("09:00").do(self.on_market_open)
            schedule.every().day.at("15:30").do(self.on_market_close)
            
            # Start trading loop
            self.trading_thread = threading.Thread(target=self.trading_loop)
            self.trading_thread.start()
            
            logger.info("Trading Agent started successfully")
            
        except Exception as e:
            logger.error(f"Error starting trading agent: {str(e)}")
    
    def stop(self):
        """Stop the trading agent"""
        try:
            logger.info("Stopping Trading Agent...")
            self.is_running = False
            
            if self.trading_thread:
                self.trading_thread.join()
            
            logger.info("Trading Agent stopped")
            
        except Exception as e:
            logger.error(f"Error stopping trading agent: {str(e)}")
    
    def trading_loop(self):
        """Main trading loop"""
        while self.is_running:
            try:
                current_time = self.data_manager.get_current_time()
                
                # Check if market is open
                if self.data_manager.is_market_open():
                    # Scan for opportunities
                    self.scan_market()
                    
                    # Monitor existing positions
                    self.monitor_positions()
                    
                    # Execute trades
                    self.execute_trades()
                
                # Sleep for 1 minute
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                time.sleep(60)
    
    def scan_market(self):
        """Scan market for trading opportunities"""
        try:
            logger.info("Scanning market for opportunities...")
            
            # Get market sentiment
            sentiment = self.data_manager.get_market_sentiment()
            logger.info(f"Market sentiment: {sentiment}")
            
            # Get volume surge stocks
            volume_surge = self.data_manager.get_volume_surge_stocks()
            logger.info(f"Volume surge stocks: {len(volume_surge)}")
            
            # Get sector performance
            sector_performance = self.data_manager.get_sector_performance()
            logger.info(f"Sector performance: {sector_performance}")
            
            # Scan stock universe for opportunities
            self.candidates = []
            
            for symbol in self.config.STOCK_UNIVERSE[:30]:  # Scan top 30 stocks
                try:
                    # Get stock data
                    data = self.data_manager.get_stock_data(symbol, period="5d")
                    if data is None or data.empty:
                        continue
                    
                    # Calculate technical indicators
                    indicators = self.technical_analyzer.get_all_indicators(data)
                    if indicators is None:
                        continue
                    
                    # Generate signals
                    signals = self.technical_analyzer.generate_signals(data, indicators)
                    
                    # Calculate risk metrics
                    risk_metrics = self.technical_analyzer.calculate_risk_metrics(data, indicators)
                    
                    # Get trend analysis
                    trend_analysis = self.technical_analyzer.get_trend_analysis(data, indicators)
                    
                    # Check if stock meets criteria
                    if self.evaluate_stock(symbol, data, indicators, signals, risk_metrics, trend_analysis, sentiment):
                        candidate = {
                            'symbol': symbol,
                            'current_price': data['Close'].iloc[-1],
                            'signals': signals,
                            'risk_metrics': risk_metrics,
                            'trend_analysis': trend_analysis,
                            'volume': data['Volume'].iloc[-1],
                            'score': self.calculate_stock_score(signals, risk_metrics, trend_analysis)
                        }
                        
                        self.candidates.append(candidate)
                        logger.info(f"Found candidate: {symbol} - Score: {candidate['score']:.2f}")
                
                except Exception as e:
                    logger.error(f"Error scanning {symbol}: {str(e)}")
                    continue
            
            # Sort candidates by score
            self.candidates.sort(key=lambda x: x['score'], reverse=True)
            logger.info(f"Found {len(self.candidates)} trading candidates")
            
        except Exception as e:
            logger.error(f"Error in market scan: {str(e)}")
    
    def evaluate_stock(self, symbol, data, indicators, signals, risk_metrics, trend_analysis, sentiment):
        """Evaluate if a stock meets trading criteria"""
        try:
            current_price = data['Close'].iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            
            # Basic filters
            if current_price < 100:  # Minimum price filter
                return False
            
            if current_volume < self.config.MIN_VOLUME_THRESHOLD:
                return False
            
            # Signal strength filter
            if abs(signals['strength']) < 0.3:  # Minimum signal strength
                return False
            
            # Risk filter
            if risk_metrics['volatility'] > 0.5:  # Maximum volatility
                return False
            
            # Trend filter
            if trend_analysis['trend'] == 'neutral':
                return False
            
            # Market sentiment filter
            if sentiment['nifty50_change'] < -1.0 and signals['strength'] > 0:
                return False  # Don't buy in strong bearish market
            
            if sentiment['nifty50_change'] > 1.0 and signals['strength'] < 0:
                return False  # Don't short in strong bullish market
            
            # Volume confirmation
            if signals['strength'] > 0 and current_volume < data['Volume'].rolling(20).mean().iloc[-1]:
                return False  # Need volume confirmation for buy signals
            
            return True
            
        except Exception as e:
            logger.error(f"Error evaluating stock {symbol}: {str(e)}")
            return False
    
    def calculate_stock_score(self, signals, risk_metrics, trend_analysis):
        """Calculate overall score for a stock"""
        try:
            score = 0
            
            # Signal strength (40% weight)
            score += signals['strength'] * 0.4
            
            # Signal confidence (20% weight)
            score += signals['confidence'] * 0.2
            
            # Trend strength (20% weight)
            if trend_analysis['trend'] == 'bullish':
                score += trend_analysis['strength'] * 0.2
            elif trend_analysis['trend'] == 'bearish':
                score -= trend_analysis['strength'] * 0.2
            
            # Risk adjustment (20% weight)
            risk_score = 1 - min(risk_metrics['volatility'], 1.0)
            score += risk_score * 0.2
            
            return score
            
        except Exception as e:
            logger.error(f"Error calculating stock score: {str(e)}")
            return 0
    
    def monitor_positions(self):
        """Monitor existing positions for exit signals"""
        try:
            for symbol in list(self.active_positions.keys()):
                try:
                    # Get current price
                    data = self.data_manager.get_stock_data(symbol, period="1d")
                    if data is None or data.empty:
                        continue
                    
                    current_price = data['Close'].iloc[-1]
                    position = self.active_positions[symbol]
                    
                    # Check stop loss
                    if self.risk_manager.check_stop_loss(symbol, current_price):
                        self.close_position(symbol, current_price, "Stop Loss")
                        continue
                    
                    # Check take profit
                    if self.risk_manager.check_take_profit(symbol, current_price):
                        self.close_position(symbol, current_price, "Take Profit")
                        continue
                    
                    # Check for exit signals
                    indicators = self.technical_analyzer.get_all_indicators(data)
                    if indicators:
                        signals = self.technical_analyzer.generate_signals(data, indicators)
                        
                        # Exit if signal turns bearish
                        if position['direction'] == 'LONG' and signals['strength'] < -0.3:
                            self.close_position(symbol, current_price, "Bearish Signal")
                        elif position['direction'] == 'SHORT' and signals['strength'] > 0.3:
                            self.close_position(symbol, current_price, "Bullish Signal")
                
                except Exception as e:
                    logger.error(f"Error monitoring position {symbol}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error monitoring positions: {str(e)}")
    
    def execute_trades(self):
        """Execute trades based on candidates"""
        try:
            # Check if we can trade
            if not self.risk_manager.check_daily_limits():
                logger.warning("Daily limits reached, skipping trade execution")
                return
            
            # Get top candidates
            top_candidates = self.candidates[:5]  # Top 5 candidates
            
            for candidate in top_candidates:
                try:
                    symbol = candidate['symbol']
                    
                    # Skip if already have position
                    if symbol in self.active_positions:
                        continue
                    
                    # Validate trade
                    current_price = candidate['current_price']
                    position_size = self.risk_manager.calculate_position_size(
                        current_price, 
                        self.config.MAX_PORTFOLIO_RISK, 
                        self.config.STOP_LOSS_PERCENTAGE
                    )
                    
                    is_valid, message = self.risk_manager.validate_trade(
                        symbol, 'BUY', position_size, current_price, candidate['risk_metrics']
                    )
                    
                    if not is_valid:
                        logger.warning(f"Trade validation failed for {symbol}: {message}")
                        continue
                    
                    # Execute trade
                    if candidate['signals']['strength'] > 0.3:  # Strong buy signal
                        self.open_position(symbol, 'LONG', position_size, current_price, candidate)
                    elif candidate['signals']['strength'] < -0.3:  # Strong sell signal
                        self.open_position(symbol, 'SHORT', position_size, current_price, candidate)
                
                except Exception as e:
                    logger.error(f"Error executing trade for {candidate['symbol']}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error executing trades: {str(e)}")
    
    def open_position(self, symbol, direction, quantity, price, candidate):
        """Open a new position"""
        try:
            logger.info(f"Opening {direction} position for {symbol} at {price:.2f}")
            
            # Update risk manager
            self.risk_manager.update_position(symbol, 'BUY', quantity, price, datetime.now())
            
            # Set stop loss and take profit
            if candidate['risk_metrics']['atr'] > 0:
                self.risk_manager.set_stop_loss_take_profit(symbol, price, candidate['risk_metrics']['atr'])
            
            # Record position
            self.active_positions[symbol] = {
                'direction': direction,
                'quantity': quantity,
                'entry_price': price,
                'entry_time': datetime.now(),
                'candidate_data': candidate
            }
            
            logger.info(f"Position opened: {symbol} {direction} {quantity} @ {price:.2f}")
            
        except Exception as e:
            logger.error(f"Error opening position for {symbol}: {str(e)}")
    
    def close_position(self, symbol, price, reason):
        """Close an existing position"""
        try:
            if symbol not in self.active_positions:
                return
            
            position = self.active_positions[symbol]
            quantity = position['quantity']
            
            logger.info(f"Closing position for {symbol} at {price:.2f} - Reason: {reason}")
            
            # Update risk manager
            self.risk_manager.update_position(symbol, 'SELL', quantity, price, datetime.now())
            
            # Remove from active positions
            del self.active_positions[symbol]
            
            logger.info(f"Position closed: {symbol} {quantity} @ {price:.2f}")
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {str(e)}")
    
    def on_market_open(self):
        """Handle market open"""
        try:
            logger.info("Market opened - Starting trading session")
            self.risk_manager.reset_daily_metrics()
            
            # Get market sentiment
            sentiment = self.data_manager.get_market_sentiment()
            logger.info(f"Market open sentiment: {sentiment}")
            
        except Exception as e:
            logger.error(f"Error on market open: {str(e)}")
    
    def on_market_close(self):
        """Handle market close"""
        try:
            logger.info("Market closed - Ending trading session")
            
            # Close all positions
            for symbol in list(self.active_positions.keys()):
                data = self.data_manager.get_stock_data(symbol, period="1d")
                if data is not None and not data.empty:
                    close_price = data['Close'].iloc[-1]
                    self.close_position(symbol, close_price, "Market Close")
            
            # Generate end-of-day report
            self.generate_daily_report()
            
        except Exception as e:
            logger.error(f"Error on market close: {str(e)}")
    
    def generate_daily_report(self):
        """Generate end-of-day trading report"""
        try:
            risk_report = self.risk_manager.get_risk_report()
            
            report = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'trading_summary': {
                    'total_trades': risk_report['current_status']['daily_trades'],
                    'daily_pnl': risk_report['current_status']['daily_pnl'],
                    'positions_closed': len(self.active_positions),
                    'candidates_found': len(self.candidates)
                },
                'portfolio_metrics': risk_report['portfolio_metrics'],
                'risk_limits': risk_report['risk_limits'],
                'market_sentiment': self.data_manager.get_market_sentiment()
            }
            
            # Save report
            filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Daily report generated: {filename}")
            
        except Exception as e:
            logger.error(f"Error generating daily report: {str(e)}")
    
    def get_status(self):
        """Get current trading agent status"""
        try:
            risk_report = self.risk_manager.get_risk_report()
            
            status = {
                'is_running': self.is_running,
                'market_open': self.data_manager.is_market_open(),
                'current_time': self.data_manager.get_current_time().strftime('%Y-%m-%d %H:%M:%S'),
                'candidates_count': len(self.candidates),
                'active_positions': len(self.active_positions),
                'portfolio_metrics': risk_report['portfolio_metrics'],
                'daily_limits': risk_report['current_status']
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting status: {str(e)}")
            return {}
    
    def get_candidates(self):
        """Get current trading candidates"""
        return self.candidates
    
    def get_positions(self):
        """Get current positions"""
        return self.active_positions