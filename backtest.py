import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf
from loguru import logger
import json

from config import TradingConfig
from data_manager import DataManager
from technical_analyzer import TechnicalAnalyzer
from risk_manager import RiskManager

class BacktestEngine:
    def __init__(self, initial_capital=1000000):
        self.config = TradingConfig()
        self.data_manager = DataManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.risk_manager = RiskManager()
        
        # Backtest state
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.positions = {}
        self.trades = []
        self.daily_returns = []
        self.equity_curve = []
        
        # Performance metrics
        self.total_return = 0
        self.sharpe_ratio = 0
        self.max_drawdown = 0
        self.win_rate = 0
        self.profit_factor = 0
        self.avg_trade = 0
        
    def run(self, start_date, end_date):
        """Run backtest for the specified period"""
        try:
            logger.info(f"Starting backtest from {start_date} to {end_date}")
            
            # Get trading dates
            trading_dates = self.get_trading_dates(start_date, end_date)
            logger.info(f"Total trading days: {len(trading_dates)}")
            
            # Initialize equity curve
            self.equity_curve = [{'date': start_date, 'equity': self.initial_capital}]
            
            # Run backtest for each trading day
            for date in trading_dates:
                self.run_daily_backtest(date)
                
                # Update equity curve
                current_equity = self.current_capital + sum([pos['unrealized_pnl'] for pos in self.positions.values()])
                self.equity_curve.append({
                    'date': date,
                    'equity': current_equity
                })
            
            # Calculate performance metrics
            self.calculate_performance_metrics()
            
            # Generate backtest report
            report = self.generate_report()
            
            logger.info("Backtest completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error in backtest: {str(e)}")
            return None
    
    def get_trading_dates(self, start_date, end_date):
        """Get list of trading dates between start and end dates"""
        try:
            # Get Nifty 50 data to determine trading dates
            nifty_data = yf.download("^NSEI", start=start_date, end=end_date)
            trading_dates = nifty_data.index.strftime('%Y-%m-%d').tolist()
            return trading_dates
        except Exception as e:
            logger.error(f"Error getting trading dates: {str(e)}")
            return []
    
    def run_daily_backtest(self, date):
        """Run backtest for a single trading day"""
        try:
            logger.info(f"Running backtest for {date}")
            
            # Reset daily metrics
            self.risk_manager.reset_daily_metrics()
            
            # Get market data for the day
            market_data = self.get_market_data(date)
            if not market_data:
                return
            
            # Scan for opportunities
            candidates = self.scan_opportunities(market_data, date)
            
            # Execute trades
            self.execute_trades(candidates, date)
            
            # Monitor existing positions
            self.monitor_positions(market_data, date)
            
            # Close positions at end of day (intraday trading)
            self.close_all_positions(market_data, date)
            
        except Exception as e:
            logger.error(f"Error in daily backtest for {date}: {str(e)}")
    
    def get_market_data(self, date):
        """Get market data for a specific date"""
        try:
            market_data = {}
            
            # Get data for stock universe
            for symbol in self.config.STOCK_UNIVERSE[:30]:  # Top 30 stocks
                try:
                    # Get historical data up to the date
                    end_date = datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1)
                    data = yf.download(symbol, start=date, end=end_date.strftime('%Y-%m-%d'))
                    
                    if not data.empty:
                        market_data[symbol] = data
                except Exception as e:
                    logger.warning(f"Error getting data for {symbol}: {str(e)}")
                    continue
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            return {}
    
    def scan_opportunities(self, market_data, date):
        """Scan for trading opportunities"""
        try:
            candidates = []
            
            for symbol, data in market_data.items():
                try:
                    if data.empty or len(data) < 20:  # Need enough data for indicators
                        continue
                    
                    # Calculate technical indicators
                    indicators = self.technical_analyzer.get_all_indicators(data)
                    if not indicators:
                        continue
                    
                    # Generate signals
                    signals = self.technical_analyzer.generate_signals(data, indicators)
                    
                    # Calculate risk metrics
                    risk_metrics = self.technical_analyzer.calculate_risk_metrics(data, indicators)
                    
                    # Get trend analysis
                    trend_analysis = self.technical_analyzer.get_trend_analysis(data, indicators)
                    
                    # Check if stock meets criteria
                    if self.evaluate_stock(symbol, data, indicators, signals, risk_metrics, trend_analysis):
                        candidate = {
                            'symbol': symbol,
                            'current_price': data['Close'].iloc[-1],
                            'signals': signals,
                            'risk_metrics': risk_metrics,
                            'trend_analysis': trend_analysis,
                            'volume': data['Volume'].iloc[-1],
                            'score': self.calculate_stock_score(signals, risk_metrics, trend_analysis)
                        }
                        
                        candidates.append(candidate)
                
                except Exception as e:
                    logger.warning(f"Error scanning {symbol}: {str(e)}")
                    continue
            
            # Sort candidates by score
            candidates.sort(key=lambda x: x['score'], reverse=True)
            return candidates
            
        except Exception as e:
            logger.error(f"Error scanning opportunities: {str(e)}")
            return []
    
    def evaluate_stock(self, symbol, data, indicators, signals, risk_metrics, trend_analysis):
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
    
    def execute_trades(self, candidates, date):
        """Execute trades based on candidates"""
        try:
            # Check if we can trade
            if not self.risk_manager.check_daily_limits():
                return
            
            # Get top candidates
            top_candidates = candidates[:5]  # Top 5 candidates
            
            for candidate in top_candidates:
                try:
                    symbol = candidate['symbol']
                    
                    # Skip if already have position
                    if symbol in self.positions:
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
                        continue
                    
                    # Execute trade
                    if candidate['signals']['strength'] > 0.3:  # Strong buy signal
                        self.open_position(symbol, 'LONG', position_size, current_price, candidate, date)
                    elif candidate['signals']['strength'] < -0.3:  # Strong sell signal
                        self.open_position(symbol, 'SHORT', position_size, current_price, candidate, date)
                
                except Exception as e:
                    logger.warning(f"Error executing trade for {candidate['symbol']}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error executing trades: {str(e)}")
    
    def open_position(self, symbol, direction, quantity, price, candidate, date):
        """Open a new position"""
        try:
            # Calculate position value
            position_value = quantity * price
            
            # Check if we have enough capital
            if position_value > self.current_capital:
                return
            
            # Update capital
            self.current_capital -= position_value
            
            # Record position
            self.positions[symbol] = {
                'direction': direction,
                'quantity': quantity,
                'entry_price': price,
                'entry_date': date,
                'position_value': position_value,
                'unrealized_pnl': 0,
                'stop_loss': None,
                'take_profit': None
            }
            
            # Set stop loss and take profit
            if candidate['risk_metrics']['atr'] > 0:
                if direction == 'LONG':
                    self.positions[symbol]['stop_loss'] = price - (candidate['risk_metrics']['atr'] * 2)
                    self.positions[symbol]['take_profit'] = price + (candidate['risk_metrics']['atr'] * 3)
                else:
                    self.positions[symbol]['stop_loss'] = price + (candidate['risk_metrics']['atr'] * 2)
                    self.positions[symbol]['take_profit'] = price - (candidate['risk_metrics']['atr'] * 3)
            
            # Record trade
            self.trades.append({
                'date': date,
                'symbol': symbol,
                'action': 'BUY',
                'direction': direction,
                'quantity': quantity,
                'price': price,
                'value': position_value
            })
            
            logger.info(f"Opened {direction} position: {symbol} {quantity} @ {price:.2f}")
            
        except Exception as e:
            logger.error(f"Error opening position for {symbol}: {str(e)}")
    
    def monitor_positions(self, market_data, date):
        """Monitor existing positions for exit signals"""
        try:
            for symbol in list(self.positions.keys()):
                try:
                    if symbol not in market_data:
                        continue
                    
                    data = market_data[symbol]
                    if data.empty:
                        continue
                    
                    current_price = data['Close'].iloc[-1]
                    position = self.positions[symbol]
                    
                    # Update unrealized P&L
                    if position['direction'] == 'LONG':
                        position['unrealized_pnl'] = (current_price - position['entry_price']) * position['quantity']
                    else:
                        position['unrealized_pnl'] = (position['entry_price'] - current_price) * position['quantity']
                    
                    # Check stop loss
                    if position['stop_loss']:
                        if position['direction'] == 'LONG' and current_price <= position['stop_loss']:
                            self.close_position(symbol, current_price, date, "Stop Loss")
                            continue
                        elif position['direction'] == 'SHORT' and current_price >= position['stop_loss']:
                            self.close_position(symbol, current_price, date, "Stop Loss")
                            continue
                    
                    # Check take profit
                    if position['take_profit']:
                        if position['direction'] == 'LONG' and current_price >= position['take_profit']:
                            self.close_position(symbol, current_price, date, "Take Profit")
                            continue
                        elif position['direction'] == 'SHORT' and current_price <= position['take_profit']:
                            self.close_position(symbol, current_price, date, "Take Profit")
                            continue
                    
                    # Check for exit signals
                    indicators = self.technical_analyzer.get_all_indicators(data)
                    if indicators:
                        signals = self.technical_analyzer.generate_signals(data, indicators)
                        
                        # Exit if signal turns opposite
                        if position['direction'] == 'LONG' and signals['strength'] < -0.3:
                            self.close_position(symbol, current_price, date, "Bearish Signal")
                        elif position['direction'] == 'SHORT' and signals['strength'] > 0.3:
                            self.close_position(symbol, current_price, date, "Bullish Signal")
                
                except Exception as e:
                    logger.warning(f"Error monitoring position {symbol}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error monitoring positions: {str(e)}")
    
    def close_position(self, symbol, price, date, reason):
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
            
            # Update capital
            position_value = quantity * price
            self.current_capital += position_value
            
            # Record trade
            self.trades.append({
                'date': date,
                'symbol': symbol,
                'action': 'SELL',
                'direction': position['direction'],
                'quantity': quantity,
                'price': price,
                'value': position_value,
                'pnl': pnl,
                'reason': reason
            })
            
            # Remove position
            del self.positions[symbol]
            
            logger.info(f"Closed position: {symbol} {quantity} @ {price:.2f} - P&L: {pnl:.2f} - Reason: {reason}")
            
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {str(e)}")
    
    def close_all_positions(self, market_data, date):
        """Close all positions at end of day (intraday trading)"""
        try:
            for symbol in list(self.positions.keys()):
                if symbol in market_data and not market_data[symbol].empty:
                    current_price = market_data[symbol]['Close'].iloc[-1]
                    self.close_position(symbol, current_price, date, "End of Day")
                else:
                    # Use entry price if no market data
                    position = self.positions[symbol]
                    self.close_position(symbol, position['entry_price'], date, "End of Day")
                    
        except Exception as e:
            logger.error(f"Error closing all positions: {str(e)}")
    
    def calculate_performance_metrics(self):
        """Calculate comprehensive performance metrics"""
        try:
            # Calculate daily returns
            for i in range(1, len(self.equity_curve)):
                prev_equity = self.equity_curve[i-1]['equity']
                curr_equity = self.equity_curve[i]['equity']
                daily_return = (curr_equity - prev_equity) / prev_equity
                self.daily_returns.append(daily_return)
            
            # Total return
            final_equity = self.equity_curve[-1]['equity']
            self.total_return = (final_equity - self.initial_capital) / self.initial_capital
            
            # Sharpe ratio
            if len(self.daily_returns) > 0:
                avg_return = np.mean(self.daily_returns)
                std_return = np.std(self.daily_returns)
                if std_return > 0:
                    self.sharpe_ratio = avg_return / std_return * np.sqrt(252)
            
            # Maximum drawdown
            peak = self.initial_capital
            self.max_drawdown = 0
            for point in self.equity_curve:
                if point['equity'] > peak:
                    peak = point['equity']
                drawdown = (peak - point['equity']) / peak
                if drawdown > self.max_drawdown:
                    self.max_drawdown = drawdown
            
            # Trade statistics
            closed_trades = [trade for trade in self.trades if trade['action'] == 'SELL' and 'pnl' in trade]
            
            if closed_trades:
                profitable_trades = [trade for trade in closed_trades if trade['pnl'] > 0]
                self.win_rate = len(profitable_trades) / len(closed_trades)
                
                total_profit = sum([trade['pnl'] for trade in profitable_trades])
                total_loss = abs(sum([trade['pnl'] for trade in closed_trades if trade['pnl'] < 0]))
                
                if total_loss > 0:
                    self.profit_factor = total_profit / total_loss
                
                self.avg_trade = np.mean([trade['pnl'] for trade in closed_trades])
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
    
    def generate_report(self):
        """Generate comprehensive backtest report"""
        try:
            report = {
                'summary': {
                    'initial_capital': self.initial_capital,
                    'final_value': self.equity_curve[-1]['equity'],
                    'total_return': self.total_return,
                    'total_return_pct': self.total_return * 100,
                    'sharpe_ratio': self.sharpe_ratio,
                    'max_drawdown': self.max_drawdown,
                    'max_drawdown_pct': self.max_drawdown * 100
                },
                'trade_statistics': {
                    'total_trades': len([trade for trade in self.trades if trade['action'] == 'SELL']),
                    'win_rate': self.win_rate,
                    'profit_factor': self.profit_factor,
                    'avg_trade': self.avg_trade
                },
                'equity_curve': self.equity_curve,
                'trades': self.trades,
                'daily_returns': self.daily_returns
            }
            
            # Save report to file
            filename = f"backtest_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Backtest report saved: {filename}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return None