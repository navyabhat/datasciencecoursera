#!/usr/bin/env python3
"""
Simplified Indian Stock Trading Agent
A basic version that works with minimal dependencies
"""

import requests
import json
import time
import threading
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleTradingAgent:
    def __init__(self):
        self.is_running = False
        self.portfolio_value = 1000000  # Starting capital in INR
        self.positions = {}
        self.daily_pnl = 0
        self.daily_trades = 0
        
        # Trading parameters
        self.max_position_size = 100000
        self.max_daily_loss = 50000
        self.max_daily_trades = 10
        self.stop_loss_percentage = 2.0
        self.take_profit_percentage = 3.0
        
        # Stock universe (Nifty 50 stocks)
        self.stock_universe = [
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
            "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
            "AXISBANK", "ASIANPAINT", "MARUTI", "HCLTECH", "SUNPHARMA",
            "TATAMOTORS", "WIPRO", "ULTRACEMCO", "TITAN", "BAJFINANCE"
        ]
        
        # Market hours (IST)
        self.market_open = "09:15"
        self.market_close = "15:30"
        
    def get_current_time(self):
        """Get current time in IST"""
        return datetime.now()
    
    def is_market_open(self):
        """Check if market is currently open"""
        current_time = self.get_current_time()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # Simple market hours check (9:15 AM to 3:30 PM IST)
        market_start = 9 * 60 + 15  # 9:15 AM
        market_end = 15 * 60 + 30   # 3:30 PM
        current_time_minutes = current_hour * 60 + current_minute
        
        return market_start <= current_time_minutes <= market_end
    
    def get_stock_price(self, symbol):
        """Get current stock price (simulated)"""
        try:
            # In a real implementation, this would fetch from a stock API
            # For demo purposes, we'll simulate prices
            import random
            base_price = {
                "RELIANCE": 2500, "TCS": 3500, "HDFCBANK": 1600, "INFY": 1500,
                "ICICIBANK": 900, "HINDUNILVR": 2500, "ITC": 400, "SBIN": 600,
                "BHARTIARTL": 800, "KOTAKBANK": 1800, "AXISBANK": 1000,
                "ASIANPAINT": 3000, "MARUTI": 10000, "HCLTECH": 1200,
                "SUNPHARMA": 1000, "TATAMOTORS": 800, "WIPRO": 500,
                "ULTRACEMCO": 8000, "TITAN": 3000, "BAJFINANCE": 7000
            }
            
            base = base_price.get(symbol, 1000)
            # Add some random variation
            variation = random.uniform(-0.02, 0.02)  # ±2% variation
            price = base * (1 + variation)
            
            return round(price, 2)
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {str(e)}")
            return None
    
    def calculate_simple_indicators(self, symbol):
        """Calculate simple technical indicators"""
        try:
            # Simulate technical analysis
            import random
            
            # Get current price
            current_price = self.get_stock_price(symbol)
            if not current_price:
                return None
            
            # Simulate RSI (0-100)
            rsi = random.uniform(20, 80)
            
            # Simulate MACD
            macd = random.uniform(-50, 50)
            macd_signal = random.uniform(-50, 50)
            
            # Simulate volume
            volume = random.uniform(1000000, 10000000)
            
            return {
                'price': current_price,
                'rsi': rsi,
                'macd': macd,
                'macd_signal': macd_signal,
                'volume': volume
            }
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {str(e)}")
            return None
    
    def generate_trading_signals(self, indicators):
        """Generate trading signals based on indicators"""
        try:
            if not indicators:
                return None
            
            signals = {
                'buy_signals': [],
                'sell_signals': [],
                'strength': 0,
                'confidence': 0
            }
            
            # RSI signals
            rsi = indicators['rsi']
            if rsi < 30:
                signals['buy_signals'].append(f"RSI oversold: {rsi:.2f}")
                signals['strength'] += 0.5
            elif rsi > 70:
                signals['sell_signals'].append(f"RSI overbought: {rsi:.2f}")
                signals['strength'] -= 0.5
            
            # MACD signals
            macd = indicators['macd']
            macd_signal = indicators['macd_signal']
            if macd > macd_signal:
                signals['buy_signals'].append("MACD bullish")
                signals['strength'] += 0.3
            else:
                signals['sell_signals'].append("MACD bearish")
                signals['strength'] -= 0.3
            
            # Volume confirmation
            volume = indicators['volume']
            if volume > 5000000:  # High volume
                if signals['strength'] > 0:
                    signals['buy_signals'].append("High volume confirmation")
                    signals['strength'] += 0.2
                elif signals['strength'] < 0:
                    signals['sell_signals'].append("High volume confirmation")
                    signals['strength'] -= 0.2
            
            # Calculate confidence
            signals['confidence'] = min(abs(signals['strength']), 1.0)
            
            return signals
        except Exception as e:
            logger.error(f"Error generating signals: {str(e)}")
            return None
    
    def scan_market(self):
        """Scan market for trading opportunities"""
        try:
            logger.info("Scanning market for opportunities...")
            
            candidates = []
            
            for symbol in self.stock_universe[:10]:  # Scan top 10 stocks
                try:
                    # Get indicators
                    indicators = self.calculate_simple_indicators(symbol)
                    if not indicators:
                        continue
                    
                    # Generate signals
                    signals = self.generate_trading_signals(indicators)
                    if not signals:
                        continue
                    
                    # Check if signal is strong enough
                    if abs(signals['strength']) >= 0.3:
                        candidate = {
                            'symbol': symbol,
                            'price': indicators['price'],
                            'signals': signals,
                            'indicators': indicators,
                            'score': signals['strength']
                        }
                        candidates.append(candidate)
                        logger.info(f"Found candidate: {symbol} - Score: {signals['strength']:.2f}")
                
                except Exception as e:
                    logger.warning(f"Error scanning {symbol}: {str(e)}")
                    continue
            
            # Sort by score
            candidates.sort(key=lambda x: abs(x['score']), reverse=True)
            logger.info(f"Found {len(candidates)} trading candidates")
            
            return candidates
        except Exception as e:
            logger.error(f"Error scanning market: {str(e)}")
            return []
    
    def execute_trades(self, candidates):
        """Execute trades based on candidates"""
        try:
            # Check daily limits
            if self.daily_trades >= self.max_daily_trades:
                logger.warning("Daily trade limit reached")
                return
            
            if self.daily_pnl <= -self.max_daily_loss:
                logger.warning("Daily loss limit reached")
                return
            
            # Execute top candidates
            for candidate in candidates[:3]:  # Top 3 candidates
                try:
                    symbol = candidate['symbol']
                    price = candidate['price']
                    signals = candidate['signals']
                    
                    # Skip if already have position
                    if symbol in self.positions:
                        continue
                    
                    # Calculate position size
                    position_value = min(self.max_position_size, self.portfolio_value * 0.1)
                    quantity = int(position_value / price)
                    
                    if quantity <= 0:
                        continue
                    
                    # Execute trade
                    if signals['strength'] > 0.3:  # Buy signal
                        self.open_position(symbol, 'LONG', quantity, price)
                    elif signals['strength'] < -0.3:  # Sell signal
                        self.open_position(symbol, 'SHORT', quantity, price)
                
                except Exception as e:
                    logger.warning(f"Error executing trade for {candidate['symbol']}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error executing trades: {str(e)}")
    
    def open_position(self, symbol, direction, quantity, price):
        """Open a new position"""
        try:
            position_value = quantity * price
            
            # Check capital
            if position_value > self.portfolio_value:
                logger.warning(f"Insufficient capital for {symbol}")
                return
            
            # Update portfolio
            self.portfolio_value -= position_value
            
            # Record position
            self.positions[symbol] = {
                'direction': direction,
                'quantity': quantity,
                'entry_price': price,
                'entry_time': self.get_current_time(),
                'position_value': position_value,
                'stop_loss': price * (1 - self.stop_loss_percentage / 100) if direction == 'LONG' else price * (1 + self.stop_loss_percentage / 100),
                'take_profit': price * (1 + self.take_profit_percentage / 100) if direction == 'LONG' else price * (1 - self.take_profit_percentage / 100)
            }
            
            self.daily_trades += 1
            
            logger.info(f"Opened {direction} position: {symbol} {quantity} @ ₹{price:.2f}")
            
        except Exception as e:
            logger.error(f"Error opening position for {symbol}: {str(e)}")
    
    def monitor_positions(self):
        """Monitor existing positions"""
        try:
            for symbol in list(self.positions.keys()):
                try:
                    current_price = self.get_stock_price(symbol)
                    if not current_price:
                        continue
                    
                    position = self.positions[symbol]
                    
                    # Check stop loss
                    if position['direction'] == 'LONG' and current_price <= position['stop_loss']:
                        self.close_position(symbol, current_price, "Stop Loss")
                        continue
                    elif position['direction'] == 'SHORT' and current_price >= position['stop_loss']:
                        self.close_position(symbol, current_price, "Stop Loss")
                        continue
                    
                    # Check take profit
                    if position['direction'] == 'LONG' and current_price >= position['take_profit']:
                        self.close_position(symbol, current_price, "Take Profit")
                        continue
                    elif position['direction'] == 'SHORT' and current_price <= position['take_profit']:
                        self.close_position(symbol, current_price, "Take Profit")
                        continue
                
                except Exception as e:
                    logger.warning(f"Error monitoring position {symbol}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error monitoring positions: {str(e)}")
    
    def close_position(self, symbol, price, reason):
        """Close an existing position"""
        try:
            if symbol not in self.positions:
                return
            
            position = self.positions[symbol]
            quantity = position['quantity']
            
            # Calculate P&L
            if position['direction'] == 'LONG':
                pnl = (price - position['entry_price']) * quantity
            else:
                pnl = (position['entry_price'] - price) * quantity
            
            # Update portfolio
            position_value = quantity * price
            self.portfolio_value += position_value
            self.daily_pnl += pnl
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(f"Closed position: {symbol} {quantity} @ ₹{price:.2f} - P&L: ₹{pnl:.2f} - Reason: {reason}")
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {str(e)}")
    
    def close_all_positions(self):
        """Close all positions at end of day"""
        try:
            for symbol in list(self.positions.keys()):
                current_price = self.get_stock_price(symbol)
                if current_price:
                    self.close_position(symbol, current_price, "End of Day")
                else:
                    # Use entry price if no current price
                    position = self.positions[symbol]
                    self.close_position(symbol, position['entry_price'], "End of Day")
                    
        except Exception as e:
            logger.error(f"Error closing all positions: {str(e)}")
    
    def trading_loop(self):
        """Main trading loop"""
        while self.is_running:
            try:
                if self.is_market_open():
                    # Scan for opportunities
                    candidates = self.scan_market()
                    
                    # Monitor existing positions
                    self.monitor_positions()
                    
                    # Execute trades
                    self.execute_trades(candidates)
                    
                    # Log status
                    logger.info(f"Portfolio: ₹{self.portfolio_value:,.2f} | Daily P&L: ₹{self.daily_pnl:,.2f} | Positions: {len(self.positions)}")
                
                # Sleep for 1 minute
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {str(e)}")
                time.sleep(60)
    
    def start(self):
        """Start the trading agent"""
        try:
            logger.info("Starting Simple Trading Agent...")
            self.is_running = True
            
            # Start trading loop in a separate thread
            self.trading_thread = threading.Thread(target=self.trading_loop)
            self.trading_thread.start()
            
            logger.info("Trading agent started successfully")
            
        except Exception as e:
            logger.error(f"Error starting trading agent: {str(e)}")
    
    def stop(self):
        """Stop the trading agent"""
        try:
            logger.info("Stopping Trading Agent...")
            self.is_running = False
            
            # Close all positions
            self.close_all_positions()
            
            if hasattr(self, 'trading_thread'):
                self.trading_thread.join()
            
            logger.info("Trading agent stopped")
            
        except Exception as e:
            logger.error(f"Error stopping trading agent: {str(e)}")
    
    def get_status(self):
        """Get current status"""
        return {
            'is_running': self.is_running,
            'market_open': self.is_market_open(),
            'portfolio_value': self.portfolio_value,
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'positions': len(self.positions),
            'current_time': self.get_current_time().strftime('%Y-%m-%d %H:%M:%S')
        }

def main():
    """Main function"""
    print("🇮🇳 Simple Indian Stock Trading Agent")
    print("=" * 50)
    
    agent = SimpleTradingAgent()
    
    try:
        # Start the agent
        agent.start()
        
        print("Trading agent is running...")
        print("Press Ctrl+C to stop")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping agent...")
        agent.stop()
        print("Agent stopped successfully")
    except Exception as e:
        print(f"Error: {str(e)}")
        agent.stop()

if __name__ == "__main__":
    main()