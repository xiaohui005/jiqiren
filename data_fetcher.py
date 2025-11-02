# data_fetcher.py
import akshare as ak
import pandas as pd
import time
import random

def fetch_stock_data(ticker, period='1mo', interval='daily'):
    """
    获取单只股票历史数据（K线专用，免费稳定）
    - ticker: 股票代码，如 '600519'（自动补 .SH/.SZ）
    - period: '1d', '5d', '1mo' 等（AKShare 自动处理）
    - interval: 'daily' 或 '5min' 等
    返回: DataFrame（空则抛异常）
    """
    try:
        time.sleep(random.uniform(0.5, 1.5))  # 防反爬

        code = ticker.replace('.SH', '').replace('.SZ', '').replace('.BJ', '').zfill(6)

        if interval == 'daily':
            # 日 K线（历史数据，前复权）
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date="20200101",  # 从 2020 开始，够用
                end_date="20251102",    # 当前日期
                adjust="qfq"  # 前复权
            )
            if df.empty:
                raise ValueError(f"股票 {code} 无历史数据（可能停牌/退市/无效代码）")
        elif 'min' in interval:
            # 分钟 K线（最近几天）
            df = ak.stock_zh_a_hist_min_em(
                symbol=code,
                period=interval.replace('min', '')  # 如 '5' for 5min
            )
            if df.empty:
                raise ValueError(f"股票 {code} 无分钟数据（交易日外或无效）")
            df['日期'] = pd.to_datetime(df['时间'])
            df = df.set_index('日期')
        else:
            raise ValueError("interval 仅支持 'daily' 或 '5min' 等")

        # 统一列名（AKShare 格式）
        df = df.rename(columns={
            '日期': 'Date',
            '开盘': 'Open',
            '最高': 'High',
            '最低': 'Low',
            '收盘': 'Close',
            '成交量': 'Volume'
        })
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date').sort_index().dropna()

        if df.empty:
            raise ValueError(f"数据解析失败：股票 {code} 无有效 K线")

        return df[['Open', 'High', 'Low', 'Close', 'Volume']].tail(60)  # 最近 60 天

    except Exception as e:
        raise RuntimeError(f"K线获取失败（股票 {ticker}）：{str(e)}。建议检查代码是否有效/活跃。")