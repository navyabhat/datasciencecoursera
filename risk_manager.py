import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger
from config import TradingConfig

class RiskManager:
    def __init__(self):
        self.config = TradingConfig()
        self.positions = {}
        self.daily_pnl = 0
        self.daily_trades = 0
        self.max_drawdown = 0
        self.portfolio_value = 1000000  # Starting portfolio value in INR
        
    def calculate_position_size(self, stock_price, risk_per_trade, stop_loss_percentage):
        """Calculate optimal position size based on risk parameters"""
        try:
            # Risk amount per trade
            risk_amount = self.portfolio_value * risk_per_trade
            
            # Stop loss amount per share
            stop_loss_amount = stock_price * (stop_loss_percentage / 100)
            
            # Position size = Risk amount / Stop loss per share
            position_size = risk_amount / stop_loss_amount
            
            # Ensure position size doesn't exceed maximum
            max_position_value = self.config.MAX_POSITION_SIZE
            max_shares = max_position_value / stock_price
            
            position_size = min(position_size, max_shares)
            
            return int(position_size)
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return 0
    
    def calculate_stop_loss(self, entry_price, atr, direction='long'):
        """Calculate dynamic stop loss based on ATR"""
        try:
            # Use 2x ATR for stop loss
            atr_stop = atr * 2
            
            if direction == 'long':
                stop_loss = entry_price - atr_stop
            else:
                stop_loss = entry_price + atr_stop
            
            return stop_loss
        except Exception as e:
            logger.error(f"Error calculating stop loss: {str(e)}")
            return None
    
    def calculate_take_profit(self, entry_price, atr, direction='long'):
        """Calculate take profit based on ATR"""
        try:
            # Use 3x ATR for take profit
            atr_target = atr * 3
            
            if direction == 'long':
                take_profit = entry_price + atr_target
            else:
                take_profit = entry_price - atr_target
            
            return take_profit
        except Exception as e:
            logger.error(f"Error calculating take profit: {str(e)}")
            return None
    
    def check_portfolio_risk(self, new_position_value):
        """Check if new position would exceed portfolio risk limits"""
        try:
            # Calculate current portfolio exposure
            total_exposure = sum([pos['value'] for pos in self.positions.values()])
            new_total_exposure = total_exposure + new_position_value
            
            # Check if new position would exceed maximum portfolio exposure
            max_exposure = self.portfolio_value * 0.8  # 80% maximum exposure
            
            if new_total_exposure > max_exposure:
                logger.warning(f"New position would exceed maximum portfolio exposure: {new_total_exposure:.2f} > {max_exposure:.2f}")
                return False
            
            # Check correlation with existing positions
            if not self.check_correlation_risk():
                logger.warning("New position would create high correlation risk")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking portfolio risk: {str(e)}")
            return False
    
    def check_correlation_risk(self):
        """Check correlation between positions to avoid over-concentration"""
        try:
            if len(self.positions) < 2:
                return True
            
            # Get stock symbols from positions
            symbols = list(self.positions.keys())
            
            # Calculate correlation matrix (simplified)
            # In a real implementation, you would use actual price data
            # For now, we'll use a simple heuristic
            sector_concentration = {}
            
            for symbol in symbols:
                # Extract sector from symbol (simplified)
                sector = self.get_stock_sector(symbol)
                if sector in sector_concentration:
                    sector_concentration[sector] += 1
                else:
                    sector_concentration[sector] = 1
            
            # Check if any sector has too many positions
            max_sector_positions = 3
            for sector, count in sector_concentration.items():
                if count > max_sector_positions:
                    logger.warning(f"Too many positions in sector {sector}: {count}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking correlation risk: {str(e)}")
            return True
    
    def get_stock_sector(self, symbol):
        """Get sector for a stock symbol (simplified mapping)"""
        sector_mapping = {
            'RELIANCE.NS': 'ENERGY',
            'TCS.NS': 'IT',
            'HDFCBANK.NS': 'BANKING',
            'INFY.NS': 'IT',
            'ICICIBANK.NS': 'BANKING',
            'HINDUNILVR.NS': 'FMCG',
            'ITC.NS': 'FMCG',
            'SBIN.NS': 'BANKING',
            'BHARTIARTL.NS': 'TELECOM',
            'KOTAKBANK.NS': 'BANKING',
            'AXISBANK.NS': 'BANKING',
            'ASIANPAINT.NS': 'CONSUMER',
            'MARUTI.NS': 'AUTO',
            'HCLTECH.NS': 'IT',
            'SUNPHARMA.NS': 'PHARMA',
            'TATAMOTORS.NS': 'AUTO',
            'WIPRO.NS': 'IT',
            'ULTRACEMCO.NS': 'CEMENT',
            'TITAN.NS': 'CONSUMER',
            'BAJFINANCE.NS': 'FINANCE'
        }
        
        return sector_mapping.get(symbol, 'OTHERS')
    
    def check_daily_limits(self):
        """Check if daily trading limits are exceeded"""
        try:
            # Check daily loss limit
            if self.daily_pnl < -self.config.MAX_DAILY_LOSS:
                logger.warning(f"Daily loss limit exceeded: {self.daily_pnl:.2f}")
                return False
            
            # Check daily trade limit
            if self.daily_trades >= self.config.MAX_DAILY_TRADES:
                logger.warning(f"Daily trade limit exceeded: {self.daily_trades}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking daily limits: {str(e)}")
            return False
    
    def update_position(self, symbol, action, quantity, price, timestamp):
        """Update position tracking"""
        try:
            if symbol not in self.positions:
                self.positions[symbol] = {
                    'quantity': 0,
                    'avg_price': 0,
                    'value': 0,
                    'pnl': 0,
                    'entry_time': None,
                    'stop_loss': None,
                    'take_profit': None
                }
            
            position = self.positions[symbol]
            
            if action == 'BUY':
                # Calculate new average price
                total_cost = (position['quantity'] * position['avg_price']) + (quantity * price)
                new_quantity = position['quantity'] + quantity
                
                if new_quantity > 0:
                    position['avg_price'] = total_cost / new_quantity
                    position['quantity'] = new_quantity
                    position['value'] = new_quantity * price
                    position['entry_time'] = timestamp
                
            elif action == 'SELL':
                # Calculate P&L
                if position['quantity'] > 0:
                    pnl = (price - position['avg_price']) * min(quantity, position['quantity'])
                    position['pnl'] += pnl
                    self.daily_pnl += pnl
                    
                    # Update quantity
                    sold_quantity = min(quantity, position['quantity'])
                    position['quantity'] -= sold_quantity
                    position['value'] = position['quantity'] * price
                    
                    # Remove position if quantity becomes 0
                    if position['quantity'] == 0:
                        del self.positions[symbol]
            
            self.daily_trades += 1
            
        except Exception as e:
            logger.error(f"Error updating position: {str(e)}")
    
    def check_stop_loss(self, symbol, current_price):
        """Check if stop loss is triggered"""
        try:
            if symbol not in self.positions:
                return False
            
            position = self.positions[symbol]
            
            if position['stop_loss'] is None:
                return False
            
            if position['quantity'] > 0:  # Long position
                if current_price <= position['stop_loss']:
                    logger.info(f"Stop loss triggered for {symbol} at {current_price}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking stop loss: {str(e)}")
            return False
    
    def check_take_profit(self, symbol, current_price):
        """Check if take profit is triggered"""
        try:
            if symbol not in self.positions:
                return False
            
            position = self.positions[symbol]
            
            if position['take_profit'] is None:
                return False
            
            if position['quantity'] > 0:  # Long position
                if current_price >= position['take_profit']:
                    logger.info(f"Take profit triggered for {symbol} at {current_price}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking take profit: {str(e)}")
            return False
    
    def calculate_portfolio_metrics(self):
        """Calculate portfolio risk metrics"""
        try:
            total_value = sum([pos['value'] for pos in self.positions.values()])
            total_pnl = sum([pos['pnl'] for pos in self.positions.values()])
            
            # Calculate portfolio volatility
            if len(self.positions) > 0:
                position_weights = [pos['value'] / total_value for pos in self.positions.values()]
                # Simplified volatility calculation
                portfolio_volatility = np.std(position_weights) * 0.2  # Assumed 20% individual volatility
            else:
                portfolio_volatility = 0
            
            # Calculate VaR (Value at Risk)
            var_95 = total_value * portfolio_volatility * 1.645  # 95% confidence level
            
            # Calculate maximum drawdown
            if total_pnl < self.max_drawdown:
                self.max_drawdown = total_pnl
            
            return {
                'total_value': total_value,
                'total_pnl': total_pnl,
                'portfolio_volatility': portfolio_volatility,
                'var_95': var_95,
                'max_drawdown': self.max_drawdown,
                'daily_pnl': self.daily_pnl,
                'daily_trades': self.daily_trades,
                'position_count': len(self.positions)
            }
        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {str(e)}")
            return {}
    
    def reset_daily_metrics(self):
        """Reset daily metrics at market open"""
        self.daily_pnl = 0
        self.daily_trades = 0
    
    def validate_trade(self, symbol, action, quantity, price, risk_metrics):
        """Validate if a trade meets risk management criteria"""
        try:
            # Check daily limits
            if not self.check_daily_limits():
                return False, "Daily limits exceeded"
            
            # Calculate position value
            position_value = quantity * price
            
            # Check portfolio risk
            if not self.check_portfolio_risk(position_value):
                return False, "Portfolio risk limits exceeded"
            
            # Check position size limits
            if position_value > self.config.MAX_POSITION_SIZE:
                return False, "Position size exceeds maximum limit"
            
            # Check if we have enough capital
            if position_value > self.portfolio_value * 0.1:  # Max 10% per position
                return False, "Position size too large relative to portfolio"
            
            return True, "Trade validated"
        except Exception as e:
            logger.error(f"Error validating trade: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    def set_stop_loss_take_profit(self, symbol, entry_price, atr):
        """Set stop loss and take profit for a position"""
        try:
            if symbol in self.positions:
                position = self.positions[symbol]
                position['stop_loss'] = self.calculate_stop_loss(entry_price, atr, 'long')
                position['take_profit'] = self.calculate_take_profit(entry_price, atr, 'long')
                
                logger.info(f"Set SL: {position['stop_loss']:.2f}, TP: {position['take_profit']:.2f} for {symbol}")
        except Exception as e:
            logger.error(f"Error setting stop loss/take profit: {str(e)}")
    
    def get_risk_report(self):
        """Generate comprehensive risk report"""
        try:
            portfolio_metrics = self.calculate_portfolio_metrics()
            
            report = {
                'portfolio_metrics': portfolio_metrics,
                'positions': self.positions,
                'risk_limits': {
                    'max_daily_loss': self.config.MAX_DAILY_LOSS,
                    'max_position_size': self.config.MAX_POSITION_SIZE,
                    'max_daily_trades': self.config.MAX_DAILY_TRADES,
                    'stop_loss_percentage': self.config.STOP_LOSS_PERCENTAGE,
                    'take_profit_percentage': self.config.TAKE_PROFIT_PERCENTAGE
                },
                'current_status': {
                    'daily_pnl': self.daily_pnl,
                    'daily_trades': self.daily_trades,
                    'position_count': len(self.positions),
                    'can_trade': self.check_daily_limits()
                }
            }
            
            return report
        except Exception as e:
            logger.error(f"Error generating risk report: {str(e)}")
            return {}