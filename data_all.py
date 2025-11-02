# data_all.py（升级版：全市场支持）
import streamlit as st
import pandas as pd
import requests
import time
import random
from io import StringIO

@st.cache_data(ttl=300)
def get_all_stocks():
    try:
        time.sleep(random.uniform(1, 2))
        
        # 函数：获取指定市场数据
        def fetch_market(node):
            url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
            params = {"page": "1", "num": "6000", "sort": "changepercent", "asc": "0", "node": node, "_": str(int(time.time() * 1000))}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Referer': 'http://finance.sina.com.cn/'}
            response = requests.get(url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            text = response.text
            if text.startswith('(') and text.endswith(')'):
                text = text[1:-1]
            return pd.read_json(StringIO(text))
        
        # 合并多市场：主板 + 创业板 + 科创板
        markets = {
            'hs_a': '主板',    # 沪深主板
            'hs_cb': '创业板', # 创业板（支持 001xxx/300xxx）
            'sh_600000': '科创板'  # 科创板（688xxx）
        }
        
        all_df = pd.DataFrame()
        for node, market in markets.items():
            df_market = fetch_market(node)
            if not df_market.empty:
                df_market['市场'] = market  # 添加标签
                all_df = pd.concat([all_df, df_market], ignore_index=True)
        
        if all_df.empty:
            return pd.DataFrame()

        # 核心字段（兼容）
        core_cols = ['code', 'name', 'trade', 'pricechange', 'changepercent', 'amount', 'volume', 'turnoverratio']
        optional_cols = {'per': '市盈率', 'pb': '市净率'}

        final_cols = [col for col in core_cols if col in all_df.columns]
        for api_col in optional_cols:
            if api_col in all_df.columns:
                final_cols.append(api_col)
        final_cols.append('市场')  # 保留市场标签

        df = all_df[final_cols].copy()

        # 重命名
        rename_map = {
            'code': '代码', 'name': '名称', 'trade': '现价',
            'pricechange': '涨跌额', 'changepercent': '涨跌幅(%)',
            'amount': '成交额', 'volume': '成交量', 'turnoverratio': '换手率(%)',
            'per': '市盈率', 'pb': '市净率'
        }
        df.rename(columns=rename_map, inplace=True)

        # 代码转为字符串
        df['代码'] = df['代码'].astype(str).str.zfill(6)

        # 格式化
        numeric_cols = ['现价', '涨跌幅(%)', '涨跌额', '成交额', '成交量', '换手率(%)']
        for col in ['市盈率', '市净率']:
            if col in df.columns:
                numeric_cols.append(col)
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df['现价'] = df['现价'].round(2)
        df['涨跌幅(%)'] = df['涨跌幅(%)'].round(2)
        df['涨跌额'] = df['涨跌额'].round(2)
        if '换手率(%)' in df.columns:
            df['换手率(%)'] = df['换手率(%)'].round(2)

        df['状态'] = df['涨跌幅(%)'].apply(lambda x: '涨' if x > 0 else ('跌' if x < 0 else '平'))
        df = df.sort_values('涨跌幅(%)', ascending=False).reset_index(drop=True)

        return df

    except Exception as e:
        st.error(f"获取失败: {str(e)[:100]}")
        return pd.DataFrame()