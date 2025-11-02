# analyzer.py
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def calculate_moving_average(data, window=20):
    data['MA'] = data['Close'].rolling(window=window).mean()
    return data

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

def plot_candlestick(data, ticker="股票"):
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="K线"
    )])
    
    if 'MA' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['MA'], mode='lines', name='20日均线', line=dict(color='orange')))
    
    if 'RSI' in data.columns:
        fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', yaxis="y2", line=dict(color='purple')))
    
    fig.update_layout(
        title=f"{ticker} 专业K线图",
        yaxis_title="价格",
        yaxis2=dict(title="RSI", overlaying="y", side="right", range=[0, 100]),
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        height=600
    )
    return fig

# 选股逻辑
def select_top_stocks(df_all, top_n=5):
    """
    从全市场选股
    条件：价格 > 50日MA, RSI < 70, 成交额 > 1亿, 市盈率 < 40
    """
    df = df_all.copy()
    
    # 过滤条件
    df = df[df['现价'] > 0]
    df = df[df['成交额'] > 1e8]  # 成交额 > 1亿
    if '市盈率' in df.columns:
        df = df[df['市盈率'] < 40]
    
    # 打分：涨跌幅 + 换手率
    df['score'] = df['涨跌幅(%)'] * 0.5 + df['换手率(%)'] * 0.5
    df = df.sort_values('score', ascending=False).head(top_n)
    
    return df[['代码', '名称', '现价', '涨跌幅(%)', '成交额', '换手率(%)', '市盈率']].reset_index(drop=True)