# news_fetcher.py
import requests
import streamlit as st
from datetime import datetime

@st.cache_data(ttl=1800)  # 30分钟刷新
def get_stock_news(ticker):
    """
    爬取东方财富新闻（免费）
    """
    try:
        code = ticker.zfill(6)
        url = f"http://api.so.eastmoney.com/bussiness/stock/news"
        params = {
            "pageindex": 1,
            "pagesize": 3,
            "code": f"{code}.{'SH' if code.startswith('6') else 'SZ'}",
            "type": "1",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'http://quote.eastmoney.com/'
        }
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        
        news = []
        for item in data.get('data', [])[:3]:
            news.append({
                'title': item['title'],
                'time': item['showtime'],
                'url': item['url']
            })
        return news
    except:
        return [{"title": "暂无新闻", "time": "", "url": ""}]