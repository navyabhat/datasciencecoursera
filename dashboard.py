import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import threading
import time

from trading_agent import TradingAgent
from data_manager import DataManager
from config import TradingConfig

# Initialize components
config = TradingConfig()
data_manager = DataManager()
trading_agent = TradingAgent()

# Initialize Dash app
app = dash.Dash(__name__, title="Indian Stock Trading Agent Dashboard")
app.config.suppress_callback_exceptions = True

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🇮🇳 Indian Stock Trading Agent", 
                style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '20px'}),
        html.Div([
            html.Button("Start Agent", id="start-btn", n_clicks=0, 
                       style={'backgroundColor': '#27ae60', 'color': 'white', 'marginRight': '10px'}),
            html.Button("Stop Agent", id="stop-btn", n_clicks=0,
                       style={'backgroundColor': '#e74c3c', 'color': 'white', 'marginRight': '10px'}),
            html.Div(id="agent-status", style={'display': 'inline-block', 'marginLeft': '20px'})
        ], style={'textAlign': 'center', 'marginBottom': '30px'})
    ]),
    
    # Main content
    html.Div([
        # Left column - Market Overview
        html.Div([
            html.H3("📊 Market Overview", style={'color': '#2c3e50'}),
            
            # Market sentiment
            html.Div([
                html.H4("Market Sentiment"),
                html.Div(id="sentiment-display")
            ], style={'marginBottom': '20px'}),
            
            # Nifty 50 chart
            html.Div([
                html.H4("Nifty 50"),
                dcc.Graph(id="nifty-chart")
            ], style={'marginBottom': '20px'}),
            
            # Sector performance
            html.Div([
                html.H4("Sector Performance"),
                dcc.Graph(id="sector-chart")
            ])
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px'}),
        
        # Right column - Trading Status
        html.Div([
            html.H3("💰 Trading Status", style={'color': '#2c3e50'}),
            
            # Portfolio metrics
            html.Div([
                html.H4("Portfolio Metrics"),
                html.Div(id="portfolio-metrics")
            ], style={'marginBottom': '20px'}),
            
            # Active positions
            html.Div([
                html.H4("Active Positions"),
                html.Div(id="positions-display")
            ], style={'marginBottom': '20px'}),
            
            # Trading candidates
            html.Div([
                html.H4("Trading Candidates"),
                html.Div(id="candidates-display")
            ])
        ], style={'width': '50%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px'})
    ]),
    
    # Bottom section - Detailed charts
    html.Div([
        html.H3("📈 Detailed Analysis", style={'color': '#2c3e50', 'textAlign': 'center'}),
        
        # Stock selector
        html.Div([
            html.Label("Select Stock:"),
            dcc.Dropdown(
                id="stock-selector",
                options=[{'label': symbol, 'value': symbol} for symbol in config.STOCK_UNIVERSE[:20]],
                value=config.STOCK_UNIVERSE[0],
                style={'width': '300px', 'margin': '10px auto'}
            )
        ], style={'textAlign': 'center', 'marginBottom': '20px'}),
        
        # Stock analysis charts
        html.Div([
            dcc.Graph(id="stock-price-chart"),
            dcc.Graph(id="technical-indicators-chart")
        ])
    ], style={'marginTop': '30px'}),
    
    # Hidden div for storing data
    html.Div(id="data-store", style={'display': 'none'}),
    
    # Auto-refresh interval
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # 30 seconds
        n_intervals=0
    )
])

# Callbacks
@app.callback(
    Output("agent-status", "children"),
    [Input("start-btn", "n_clicks"),
     Input("stop-btn", "n_clicks")]
)
def control_agent(start_clicks, stop_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return html.Span("Agent Status: Stopped", style={'color': 'red'})
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == "start-btn" and start_clicks > 0:
        try:
            trading_agent.start()
            return html.Span("Agent Status: Running", style={'color': 'green'})
        except Exception as e:
            return html.Span(f"Error: {str(e)}", style={'color': 'red'})
    
    elif button_id == "stop-btn" and stop_clicks > 0:
        try:
            trading_agent.stop()
            return html.Span("Agent Status: Stopped", style={'color': 'red'})
        except Exception as e:
            return html.Span(f"Error: {str(e)}", style={'color': 'red'})
    
    return html.Span("Agent Status: Stopped", style={'color': 'red'})

@app.callback(
    Output("sentiment-display", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_sentiment(n):
    try:
        sentiment = data_manager.get_market_sentiment()
        
        return html.Div([
            html.Div([
                html.Span("Nifty 50: "),
                html.Span(f"{sentiment['nifty50_change']:.2f}%", 
                         style={'color': 'green' if sentiment['nifty50_change'] > 0 else 'red'})
            ]),
            html.Div([
                html.Span("Bank Nifty: "),
                html.Span(f"{sentiment['bank_nifty_change']:.2f}%",
                         style={'color': 'green' if sentiment['bank_nifty_change'] > 0 else 'red'})
            ]),
            html.Div([
                html.Span("VIX: "),
                html.Span(f"{sentiment['vix']:.2f}")
            ])
        ])
    except Exception as e:
        return html.Div(f"Error loading sentiment: {str(e)}")

@app.callback(
    Output("nifty-chart", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_nifty_chart(n):
    try:
        # Get Nifty 50 data
        nifty_data = data_manager.get_stock_data("^NSEI", period="5d")
        
        if nifty_data is None or nifty_data.empty:
            return go.Figure()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=nifty_data.index,
            y=nifty_data['Close'],
            mode='lines',
            name='Nifty 50',
            line=dict(color='#3498db', width=2)
        ))
        
        fig.update_layout(
            title="Nifty 50 - 5 Day Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            height=300,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    except Exception as e:
        return go.Figure()

@app.callback(
    Output("sector-chart", "figure"),
    [Input("interval-component", "n_intervals")]
)
def update_sector_chart(n):
    try:
        sector_performance = data_manager.get_sector_performance()
        
        if not sector_performance:
            return go.Figure()
        
        sectors = list(sector_performance.keys())
        values = list(sector_performance.values())
        colors = ['green' if v > 0 else 'red' for v in values]
        
        fig = go.Figure(data=[
            go.Bar(
                x=sectors,
                y=values,
                marker_color=colors
            )
        ])
        
        fig.update_layout(
            title="Sector Performance",
            xaxis_title="Sector",
            yaxis_title="Change (%)",
            height=300,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    except Exception as e:
        return go.Figure()

@app.callback(
    Output("portfolio-metrics", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_portfolio_metrics(n):
    try:
        status = trading_agent.get_status()
        portfolio_metrics = status.get('portfolio_metrics', {})
        
        return html.Div([
            html.Div([
                html.Span("Total Value: "),
                html.Span(f"₹{portfolio_metrics.get('total_value', 0):,.2f}")
            ]),
            html.Div([
                html.Span("Daily P&L: "),
                html.Span(f"₹{portfolio_metrics.get('daily_pnl', 0):,.2f}",
                         style={'color': 'green' if portfolio_metrics.get('daily_pnl', 0) > 0 else 'red'})
            ]),
            html.Div([
                html.Span("Positions: "),
                html.Span(f"{portfolio_metrics.get('position_count', 0)}")
            ]),
            html.Div([
                html.Span("Max Drawdown: "),
                html.Span(f"₹{portfolio_metrics.get('max_drawdown', 0):,.2f}",
                         style={'color': 'red'})
            ])
        ])
    except Exception as e:
        return html.Div(f"Error loading portfolio metrics: {str(e)}")

@app.callback(
    Output("positions-display", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_positions(n):
    try:
        positions = trading_agent.get_positions()
        
        if not positions:
            return html.Div("No active positions")
        
        position_cards = []
        for symbol, position in positions.items():
            card = html.Div([
                html.H5(symbol),
                html.Div([
                    html.Span(f"Direction: {position['direction']}"),
                    html.Br(),
                    html.Span(f"Quantity: {position['quantity']}"),
                    html.Br(),
                    html.Span(f"Entry Price: ₹{position['entry_price']:.2f}")
                ])
            ], style={
                'border': '1px solid #ddd',
                'padding': '10px',
                'margin': '5px',
                'borderRadius': '5px',
                'backgroundColor': '#f8f9fa'
            })
            position_cards.append(card)
        
        return html.Div(position_cards)
    except Exception as e:
        return html.Div(f"Error loading positions: {str(e)}")

@app.callback(
    Output("candidates-display", "children"),
    [Input("interval-component", "n_intervals")]
)
def update_candidates(n):
    try:
        candidates = trading_agent.get_candidates()
        
        if not candidates:
            return html.Div("No trading candidates found")
        
        candidate_cards = []
        for candidate in candidates[:5]:  # Show top 5 candidates
            card = html.Div([
                html.H5(candidate['symbol']),
                html.Div([
                    html.Span(f"Price: ₹{candidate['current_price']:.2f}"),
                    html.Br(),
                    html.Span(f"Score: {candidate['score']:.2f}"),
                    html.Br(),
                    html.Span(f"Signal Strength: {candidate['signals']['strength']:.2f}")
                ])
            ], style={
                'border': '1px solid #ddd',
                'padding': '10px',
                'margin': '5px',
                'borderRadius': '5px',
                'backgroundColor': '#f8f9fa'
            })
            candidate_cards.append(card)
        
        return html.Div(candidate_cards)
    except Exception as e:
        return html.Div(f"Error loading candidates: {str(e)}")

@app.callback(
    Output("stock-price-chart", "figure"),
    [Input("stock-selector", "value"),
     Input("interval-component", "n_intervals")]
)
def update_stock_price_chart(symbol, n):
    try:
        if not symbol:
            return go.Figure()
        
        # Get stock data
        data = data_manager.get_stock_data(symbol, period="5d")
        
        if data is None or data.empty:
            return go.Figure()
        
        fig = go.Figure()
        
        # Candlestick chart
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name=symbol
        ))
        
        fig.update_layout(
            title=f"{symbol} - 5 Day Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            height=400,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    except Exception as e:
        return go.Figure()

@app.callback(
    Output("technical-indicators-chart", "figure"),
    [Input("stock-selector", "value"),
     Input("interval-component", "n_intervals")]
)
def update_technical_indicators(symbol, n):
    try:
        if not symbol:
            return go.Figure()
        
        # Get stock data
        data = data_manager.get_stock_data(symbol, period="5d")
        
        if data is None or data.empty:
            return go.Figure()
        
        # Calculate technical indicators
        from technical_analyzer import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer()
        indicators = analyzer.get_all_indicators(data)
        
        if not indicators:
            return go.Figure()
        
        # Create subplots
        from plotly.subplots import make_subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Price & Bollinger Bands', 'RSI', 'MACD'),
            vertical_spacing=0.1
        )
        
        # Price and Bollinger Bands
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#2c3e50')
        ), row=1, col=1)
        
        if indicators['bollinger']:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['bollinger']['upper'],
                mode='lines',
                name='Upper BB',
                line=dict(color='#e74c3c', dash='dash')
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['bollinger']['lower'],
                mode='lines',
                name='Lower BB',
                line=dict(color='#e74c3c', dash='dash'),
                fill='tonexty'
            ), row=1, col=1)
        
        # RSI
        if indicators['rsi'] is not None:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['rsi'],
                mode='lines',
                name='RSI',
                line=dict(color='#9b59b6')
            ), row=2, col=1)
            
            # Add overbought/oversold lines
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        if indicators['macd']:
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['macd']['macd'],
                mode='lines',
                name='MACD',
                line=dict(color='#3498db')
            ), row=3, col=1)
            
            fig.add_trace(go.Scatter(
                x=data.index,
                y=indicators['macd']['macd_signal'],
                mode='lines',
                name='Signal',
                line=dict(color='#e67e22')
            ), row=3, col=1)
        
        fig.update_layout(
            title=f"{symbol} - Technical Indicators",
            height=600,
            margin=dict(l=50, r=50, t=50, b=50)
        )
        
        return fig
    except Exception as e:
        return go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)