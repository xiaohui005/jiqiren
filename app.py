# app.py
import streamlit as st
import plotly.graph_objects as go
from data_all import get_all_stocks
from data_fetcher import fetch_stock_data
from analyzer import calculate_moving_average, calculate_rsi, plot_candlestick, select_top_stocks
from news_fetcher import get_stock_news

st.set_page_config(page_title="智能A股选股系统", layout="wide")

st.title("智能A股选股系统")
st.caption("技术分析 + 实时新闻 + 自动推荐 | 数据每5分钟更新")

# 左侧：全市场 + 推荐
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("潜力股推荐（今日Top5）")
    df_all = get_all_stocks()
    if not df_all.empty:
        top_stocks = select_top_stocks(df_all, top_n=5)
        st.dataframe(top_stocks.style.format({
            '现价': '{:.2f}',
            '涨跌幅(%)': '{:.2f}',
            '成交额': '{:,.0f}',
            '换手率(%)': '{:.2f}',
            '市盈率': '{:.2f}'
        }), use_container_width=True)
        
        # 选股理由
        st.info("""
        **选股逻辑**：  
        - 价格 > 20日均线  
        - RSI < 70（非超买）  
        - 成交额 > 1亿  
        - 市盈率 < 40  
        - 涨跌幅 + 换手率 加权打分
        """)
    else:
        st.warning("暂无数据")

with col2:
    st.subheader("个股深度分析")
    code = st.text_input("输入股票代码", "600519")
    if st.button("分析"):
        with st.spinner("加载中..."):
            try:
                # 获取历史数据
                data = fetch_stock_data(code, interval='daily')
                data = calculate_moving_average(data)
                data = calculate_rsi(data)
                
                # K线图
                fig = plot_candlestick(data, f"{code} {data.index[-1].strftime('%Y-%m-%d')}")
                st.plotly_chart(fig, use_container_width=True)
                
                # 最新指标
                latest = data.iloc[-1]
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("最新价", f"{latest['Close']:.2f}")
                col_b.metric("20日均线", f"{latest['MA']:.2f}")
                col_c.metric("RSI", f"{latest['RSI']:.1f}")
                
                # 新闻
                st.subheader("实时新闻")
                news = get_stock_news(code)
                for n in news:
                    if n['url']:
                        st.markdown(f"**{n['time']}** [{n['title']}]({n['url']})")
                    else:
                        st.write(f"**{n['time']}** {n['title']}")
                        
            except Exception as e:
                st.error(f"分析失败: {e}")