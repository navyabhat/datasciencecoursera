import pandas as pd
import numpy as np
import ta
from loguru import logger
from config import TradingConfig

class TechnicalAnalyzer:
    def __init__(self):
        self.config = TradingConfig()
        
    def calculate_rsi(self, data, period=14):
        """Calculate Relative Strength Index"""
        try:
            rsi = ta.momentum.RSIIndicator(data['Close'], window=period)
            return rsi.rsi()
        except Exception as e:
            logger.error(f"Error calculating RSI: {str(e)}")
            return None
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        try:
            macd = ta.trend.MACD(data['Close'], window_fast=fast, window_slow=slow, window_sign=signal)
            return {
                'macd': macd.macd(),
                'macd_signal': macd.macd_signal(),
                'macd_histogram': macd.macd_diff()
            }
        except Exception as e:
            logger.error(f"Error calculating MACD: {str(e)}")
            return None
    
    def calculate_bollinger_bands(self, data, period=20, std=2):
        """Calculate Bollinger Bands"""
        try:
            bb = ta.volatility.BollingerBands(data['Close'], window=period, window_dev=std)
            return {
                'upper': bb.bollinger_hband(),
                'middle': bb.bollinger_mavg(),
                'lower': bb.bollinger_lband(),
                'width': bb.bollinger_wband(),
                'percent': bb.bollinger_pband()
            }
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {str(e)}")
            return None
    
    def calculate_stochastic(self, data, k_period=14, d_period=3):
        """Calculate Stochastic Oscillator"""
        try:
            stoch = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close'], 
                                                    window=k_period, smooth_window=d_period)
            return {
                'k': stoch.stoch(),
                'd': stoch.stoch_signal()
            }
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {str(e)}")
            return None
    
    def calculate_atr(self, data, period=14):
        """Calculate Average True Range"""
        try:
            atr = ta.volatility.AverageTrueRange(data['High'], data['Low'], data['Close'], window=period)
            return atr.average_true_range()
        except Exception as e:
            logger.error(f"Error calculating ATR: {str(e)}")
            return None
    
    def calculate_ema(self, data, periods=[9, 21, 50, 200]):
        """Calculate Exponential Moving Averages"""
        try:
            ema_data = {}
            for period in periods:
                ema = ta.trend.EMAIndicator(data['Close'], window=period)
                ema_data[f'ema_{period}'] = ema.ema_indicator()
            return ema_data
        except Exception as e:
            logger.error(f"Error calculating EMA: {str(e)}")
            return None
    
    def calculate_sma(self, data, periods=[20, 50, 200]):
        """Calculate Simple Moving Averages"""
        try:
            sma_data = {}
            for period in periods:
                sma = ta.trend.SMAIndicator(data['Close'], window=period)
                sma_data[f'sma_{period}'] = sma.sma_indicator()
            return sma_data
        except Exception as e:
            logger.error(f"Error calculating SMA: {str(e)}")
            return None
    
    def calculate_volume_indicators(self, data):
        """Calculate volume-based indicators"""
        try:
            # Volume SMA
            volume_sma = ta.volume.volume_sma(data['Close'], data['Volume'], window=20)
            
            # On Balance Volume
            obv = ta.volume.OnBalanceVolumeIndicator(data['Close'], data['Volume'])
            
            # Volume Rate of Change
            vroc = ta.volume.VolumeRateOfChangeIndicator(data['Volume'], window=25)
            
            return {
                'volume_sma': volume_sma,
                'obv': obv.on_balance_volume(),
                'vroc': vroc.volume_rate_of_change()
            }
        except Exception as e:
            logger.error(f"Error calculating volume indicators: {str(e)}")
            return None
    
    def calculate_momentum_indicators(self, data):
        """Calculate momentum indicators"""
        try:
            # Williams %R
            williams_r = ta.momentum.WilliamsRIndicator(data['High'], data['Low'], data['Close'])
            
            # Commodity Channel Index
            cci = ta.trend.CCIIndicator(data['High'], data['Low'], data['Close'])
            
            # Money Flow Index
            mfi = ta.volume.MFIIndicator(data['High'], data['Low'], data['Close'], data['Volume'])
            
            return {
                'williams_r': williams_r.williams_r(),
                'cci': cci.cci(),
                'mfi': mfi.money_flow_index()
            }
        except Exception as e:
            logger.error(f"Error calculating momentum indicators: {str(e)}")
            return None
    
    def get_all_indicators(self, data):
        """Calculate all technical indicators for a stock"""
        if data is None or data.empty:
            return None
        
        indicators = {}
        
        # Basic indicators
        indicators['rsi'] = self.calculate_rsi(data, self.config.RSI_PERIOD)
        indicators['macd'] = self.calculate_macd(data, self.config.MACD_FAST, 
                                               self.config.MACD_SLOW, self.config.MACD_SIGNAL)
        indicators['bollinger'] = self.calculate_bollinger_bands(data, self.config.BOLLINGER_PERIOD, 
                                                               self.config.BOLLINGER_STD)
        indicators['stochastic'] = self.calculate_stochastic(data)
        indicators['atr'] = self.calculate_atr(data)
        indicators['ema'] = self.calculate_ema(data)
        indicators['sma'] = self.calculate_sma(data)
        indicators['volume'] = self.calculate_volume_indicators(data)
        indicators['momentum'] = self.calculate_momentum_indicators(data)
        
        return indicators
    
    def generate_signals(self, data, indicators):
        """Generate trading signals based on technical indicators"""
        signals = {
            'buy_signals': [],
            'sell_signals': [],
            'strength': 0,
            'confidence': 0
        }
        
        if data is None or indicators is None:
            return signals
        
        current_price = data['Close'].iloc[-1]
        signal_strength = 0
        total_signals = 0
        
        # RSI Signals
        if indicators['rsi'] is not None:
            rsi_value = indicators['rsi'].iloc[-1]
            if not pd.isna(rsi_value):
                if rsi_value < self.config.RSI_OVERSOLD:
                    signals['buy_signals'].append(f"RSI oversold: {rsi_value:.2f}")
                    signal_strength += 1
                elif rsi_value > self.config.RSI_OVERBOUGHT:
                    signals['sell_signals'].append(f"RSI overbought: {rsi_value:.2f}")
                    signal_strength -= 1
                total_signals += 1
        
        # MACD Signals
        if indicators['macd'] is not None:
            macd_value = indicators['macd']['macd'].iloc[-1]
            macd_signal = indicators['macd']['macd_signal'].iloc[-1]
            if not pd.isna(macd_value) and not pd.isna(macd_signal):
                if macd_value > macd_signal:
                    signals['buy_signals'].append("MACD bullish crossover")
                    signal_strength += 1
                elif macd_value < macd_signal:
                    signals['sell_signals'].append("MACD bearish crossover")
                    signal_strength -= 1
                total_signals += 1
        
        # Bollinger Bands Signals
        if indicators['bollinger'] is not None:
            bb_upper = indicators['bollinger']['upper'].iloc[-1]
            bb_lower = indicators['bollinger']['lower'].iloc[-1]
            bb_percent = indicators['bollinger']['percent'].iloc[-1]
            
            if not pd.isna(bb_upper) and not pd.isna(bb_lower):
                if current_price <= bb_lower:
                    signals['buy_signals'].append("Price at Bollinger lower band")
                    signal_strength += 1
                elif current_price >= bb_upper:
                    signals['sell_signals'].append("Price at Bollinger upper band")
                    signal_strength -= 1
                total_signals += 1
        
        # Moving Average Signals
        if indicators['ema'] is not None:
            ema_9 = indicators['ema']['ema_9'].iloc[-1]
            ema_21 = indicators['ema']['ema_21'].iloc[-1]
            
            if not pd.isna(ema_9) and not pd.isna(ema_21):
                if ema_9 > ema_21:
                    signals['buy_signals'].append("EMA 9 > EMA 21 (bullish)")
                    signal_strength += 1
                else:
                    signals['sell_signals'].append("EMA 9 < EMA 21 (bearish)")
                    signal_strength -= 1
                total_signals += 1
        
        # Stochastic Signals
        if indicators['stochastic'] is not None:
            stoch_k = indicators['stochastic']['k'].iloc[-1]
            stoch_d = indicators['stochastic']['d'].iloc[-1]
            
            if not pd.isna(stoch_k) and not pd.isna(stoch_d):
                if stoch_k < 20 and stoch_d < 20:
                    signals['buy_signals'].append("Stochastic oversold")
                    signal_strength += 1
                elif stoch_k > 80 and stoch_d > 80:
                    signals['sell_signals'].append("Stochastic overbought")
                    signal_strength -= 1
                total_signals += 1
        
        # Volume Analysis
        if indicators['volume'] is not None and 'volume_sma' in indicators['volume']:
            volume_sma = indicators['volume']['volume_sma'].iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            
            if not pd.isna(volume_sma) and current_volume > volume_sma * 1.5:
                if signal_strength > 0:
                    signals['buy_signals'].append("High volume confirmation")
                    signal_strength += 0.5
                elif signal_strength < 0:
                    signals['sell_signals'].append("High volume confirmation")
                    signal_strength -= 0.5
                total_signals += 1
        
        # Calculate overall signal strength and confidence
        if total_signals > 0:
            signals['strength'] = signal_strength / total_signals
            signals['confidence'] = min(abs(signal_strength) / total_signals, 1.0)
        
        return signals
    
    def calculate_risk_metrics(self, data, indicators):
        """Calculate risk metrics for position sizing"""
        risk_metrics = {
            'volatility': 0,
            'atr': 0,
            'max_loss': 0,
            'position_size': 0
        }
        
        if data is None or indicators is None:
            return risk_metrics
        
        # Calculate volatility (standard deviation of returns)
        returns = data['Close'].pct_change().dropna()
        if len(returns) > 0:
            risk_metrics['volatility'] = returns.std() * np.sqrt(252)  # Annualized
        
        # ATR for stop loss calculation
        if indicators['atr'] is not None:
            atr_value = indicators['atr'].iloc[-1]
            if not pd.isna(atr_value):
                risk_metrics['atr'] = atr_value
        
        # Calculate maximum loss based on ATR
        current_price = data['Close'].iloc[-1]
        if risk_metrics['atr'] > 0:
            risk_metrics['max_loss'] = current_price - (risk_metrics['atr'] * 2)
        
        # Calculate position size based on risk
        if risk_metrics['max_loss'] > 0:
            risk_per_trade = self.config.MAX_POSITION_SIZE * self.config.MAX_PORTFOLIO_RISK
            risk_metrics['position_size'] = risk_per_trade / (current_price - risk_metrics['max_loss'])
        
        return risk_metrics
    
    def get_trend_analysis(self, data, indicators):
        """Analyze overall trend direction"""
        trend_analysis = {
            'trend': 'neutral',
            'strength': 0,
            'support': 0,
            'resistance': 0
        }
        
        if data is None or indicators is None:
            return trend_analysis
        
        current_price = data['Close'].iloc[-1]
        trend_signals = 0
        total_trend_indicators = 0
        
        # EMA trend analysis
        if indicators['ema'] is not None:
            ema_9 = indicators['ema']['ema_9'].iloc[-1]
            ema_21 = indicators['ema']['ema_21'].iloc[-1]
            ema_50 = indicators['ema']['ema_50'].iloc[-1]
            
            if not pd.isna(ema_9) and not pd.isna(ema_21) and not pd.isna(ema_50):
                if ema_9 > ema_21 > ema_50:
                    trend_signals += 1
                elif ema_9 < ema_21 < ema_50:
                    trend_signals -= 1
                total_trend_indicators += 1
        
        # Price vs moving averages
        if indicators['sma'] is not None:
            sma_20 = indicators['sma']['sma_20'].iloc[-1]
            sma_50 = indicators['sma']['sma_50'].iloc[-1]
            
            if not pd.isna(sma_20) and not pd.isna(sma_50):
                if current_price > sma_20 > sma_50:
                    trend_signals += 1
                elif current_price < sma_20 < sma_50:
                    trend_signals -= 1
                total_trend_indicators += 1
        
        # MACD trend
        if indicators['macd'] is not None:
            macd_value = indicators['macd']['macd'].iloc[-1]
            if not pd.isna(macd_value):
                if macd_value > 0:
                    trend_signals += 1
                else:
                    trend_signals -= 1
                total_trend_indicators += 1
        
        # Determine trend
        if total_trend_indicators > 0:
            trend_strength = trend_signals / total_trend_indicators
            
            if trend_strength > 0.3:
                trend_analysis['trend'] = 'bullish'
                trend_analysis['strength'] = trend_strength
            elif trend_strength < -0.3:
                trend_analysis['trend'] = 'bearish'
                trend_analysis['strength'] = abs(trend_strength)
            else:
                trend_analysis['trend'] = 'neutral'
                trend_analysis['strength'] = abs(trend_strength)
        
        # Support and resistance levels
        if indicators['bollinger'] is not None:
            bb_lower = indicators['bollinger']['lower'].iloc[-1]
            bb_upper = indicators['bollinger']['upper'].iloc[-1]
            
            if not pd.isna(bb_lower):
                trend_analysis['support'] = bb_lower
            if not pd.isna(bb_upper):
                trend_analysis['resistance'] = bb_upper
        
        return trend_analysis