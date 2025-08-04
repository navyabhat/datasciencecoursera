import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import requests
from bs4 import BeautifulSoup
import time
from loguru import logger
from config import TradingConfig

class DataManager:
    def __init__(self):
        self.config = TradingConfig()
        self.indian_tz = pytz.timezone(self.config.MARKET_TIMEZONE)
        self.cache = {}
        self.cache_timeout = 60  # 1 minute cache
        
    def get_current_time(self):
        """Get current time in Indian timezone"""
        return datetime.now(self.indian_tz)
    
    def is_market_open(self):
        """Check if Indian market is currently open"""
        current_time = self.get_current_time()
        market_open = datetime.strptime(self.config.MARKET_OPEN_TIME, "%H:%M").time()
        market_close = datetime.strptime(self.config.MARKET_CLOSE_TIME, "%H:%M").time()
        
        return market_open <= current_time.time() <= market_close
    
    def get_stock_data(self, symbol, period="1d", interval="1m"):
        """Get real-time stock data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data received for {symbol}")
                return None
                
            return data
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_historical_data(self, symbol, start_date, end_date):
        """Get historical stock data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date)
            return data
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
            return None
    
    def get_market_sentiment(self):
        """Get market sentiment from various sources"""
        sentiment_data = {
            'nifty50_change': 0,
            'bank_nifty_change': 0,
            'fii_dii_flow': 0,
            'vix': 0
        }
        
        try:
            # Get Nifty 50 data
            nifty_data = self.get_stock_data("^NSEI", period="2d")
            if nifty_data is not None and len(nifty_data) >= 2:
                current_price = nifty_data['Close'].iloc[-1]
                prev_price = nifty_data['Close'].iloc[-2]
                sentiment_data['nifty50_change'] = ((current_price - prev_price) / prev_price) * 100
            
            # Get Bank Nifty data
            bank_nifty_data = self.get_stock_data("^NSEBANK", period="2d")
            if bank_nifty_data is not None and len(bank_nifty_data) >= 2:
                current_price = bank_nifty_data['Close'].iloc[-1]
                prev_price = bank_nifty_data['Close'].iloc[-2]
                sentiment_data['bank_nifty_change'] = ((current_price - prev_price) / prev_price) * 100
            
            # Get VIX data
            vix_data = self.get_stock_data("^INDIAVIX", period="1d")
            if vix_data is not None:
                sentiment_data['vix'] = vix_data['Close'].iloc[-1]
                
        except Exception as e:
            logger.error(f"Error fetching market sentiment: {str(e)}")
        
        return sentiment_data
    
    def get_top_gainers_losers(self):
        """Get top gainers and losers from NSE"""
        try:
            url = "https://www.nseindia.com/api/equity-stockIndices?index=SECURITIES%20IN%20F%26O"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                stocks = data.get('data', [])
                
                # Sort by change percentage
                sorted_stocks = sorted(stocks, key=lambda x: float(x.get('pChange', 0)), reverse=True)
                
                top_gainers = sorted_stocks[:10]
                top_losers = sorted_stocks[-10:]
                
                return {
                    'gainers': top_gainers,
                    'losers': top_losers
                }
        except Exception as e:
            logger.error(f"Error fetching top gainers/losers: {str(e)}")
        
        return {'gainers': [], 'losers': []}
    
    def get_volume_surge_stocks(self):
        """Get stocks with unusual volume surge"""
        volume_surge_stocks = []
        
        for symbol in self.config.STOCK_UNIVERSE[:20]:  # Check top 20 stocks
            try:
                data = self.get_stock_data(symbol, period="5d")
                if data is not None and len(data) >= 5:
                    current_volume = data['Volume'].iloc[-1]
                    avg_volume = data['Volume'].iloc[-5:].mean()
                    
                    if current_volume > avg_volume * self.config.VOLUME_SURGE_THRESHOLD:
                        volume_surge_stocks.append({
                            'symbol': symbol,
                            'current_volume': current_volume,
                            'avg_volume': avg_volume,
                            'surge_ratio': current_volume / avg_volume
                        })
            except Exception as e:
                logger.error(f"Error checking volume surge for {symbol}: {str(e)}")
        
        return sorted(volume_surge_stocks, key=lambda x: x['surge_ratio'], reverse=True)
    
    def get_sector_performance(self):
        """Get sector-wise performance"""
        sectors = {
            'BANKING': ['HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'KOTAKBANK.NS', 'AXISBANK.NS'],
            'IT': ['TCS.NS', 'INFY.NS', 'HCLTECH.NS', 'WIPRO.NS', 'TECHM.NS'],
            'AUTO': ['MARUTI.NS', 'TATAMOTORS.NS', 'HEROMOTOCO.NS', 'EICHERMOT.NS', 'M&M.NS'],
            'PHARMA': ['SUNPHARMA.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'DRREDDY.NS'],
            'ENERGY': ['RELIANCE.NS', 'ONGC.NS', 'NTPC.NS', 'POWERGRID.NS', 'BPCL.NS']
        }
        
        sector_performance = {}
        
        for sector, stocks in sectors.items():
            sector_change = 0
            valid_stocks = 0
            
            for stock in stocks:
                data = self.get_stock_data(stock, period="2d")
                if data is not None and len(data) >= 2:
                    current_price = data['Close'].iloc[-1]
                    prev_price = data['Close'].iloc[-2]
                    change = ((current_price - prev_price) / prev_price) * 100
                    sector_change += change
                    valid_stocks += 1
            
            if valid_stocks > 0:
                sector_performance[sector] = sector_change / valid_stocks
        
        return sector_performance
    
    def get_support_resistance(self, symbol, period=20):
        """Calculate support and resistance levels"""
        try:
            data = self.get_stock_data(symbol, period=f"{period}d")
            if data is None or len(data) < period:
                return None
            
            high = data['High'].max()
            low = data['Low'].min()
            close = data['Close'].iloc[-1]
            
            # Pivot points
            pivot = (high + low + close) / 3
            r1 = 2 * pivot - low
            s1 = 2 * pivot - high
            r2 = pivot + (high - low)
            s2 = pivot - (high - low)
            
            return {
                'pivot': pivot,
                'r1': r1, 'r2': r2,
                's1': s1, 's2': s2,
                'high': high, 'low': low
            }
        except Exception as e:
            logger.error(f"Error calculating support/resistance for {symbol}: {str(e)}")
            return None
    
    def get_market_breadth(self):
        """Calculate market breadth indicators"""
        try:
            # Get Nifty 50 components performance
            advancing = 0
            declining = 0
            
            for symbol in self.config.STOCK_UNIVERSE[:50]:
                data = self.get_stock_data(symbol, period="2d")
                if data is not None and len(data) >= 2:
                    current_price = data['Close'].iloc[-1]
                    prev_price = data['Close'].iloc[-2]
                    
                    if current_price > prev_price:
                        advancing += 1
                    elif current_price < prev_price:
                        declining += 1
            
            total_stocks = advancing + declining
            if total_stocks > 0:
                advance_decline_ratio = advancing / declining if declining > 0 else float('inf')
                breadth = (advancing - declining) / total_stocks
            else:
                advance_decline_ratio = 1
                breadth = 0
            
            return {
                'advancing': advancing,
                'declining': declining,
                'advance_decline_ratio': advance_decline_ratio,
                'breadth': breadth
            }
        except Exception as e:
            logger.error(f"Error calculating market breadth: {str(e)}")
            return None