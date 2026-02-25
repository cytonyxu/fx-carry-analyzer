import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import datetime

st.set_page_config(page_title="FX Carry Trade $1M Analyzer", layout="wide")
st.title("FX Carry Trade & Risk Analyzer")

st.sidebar.header("Portfolio Settings")
capital = st.sidebar.number_input("Initial Capital ($)", value=1000000, step=100000)
tickers_input = st.sidebar.text_input("Yahoo Finance Tickers", "USDJPY=X, MXNJPY=X, AUDJPY=X, ZARJPY=X")
tickers = [t.strip() for t in tickers_input.split(',')]
annual_spread = st.sidebar.number_input("Net Interest Spread (%)", value=5.5, step=0.1) / 100
years = st.sidebar.slider("Years of Data", 1, 10, 5)

if st.sidebar.button("Run Analysis"):
    # 1. CARRY PROFIT
    st.header("1. Interest Income (The 'Carry')")
    col1, col2, col3 = st.columns(3)
    col1.metric("Initial Capital", f"${capital:,.2f}")
    col2.metric("Annual Spread", f"{annual_spread*100:.2f}%")
    col3.metric("Annual Income", f"${capital * annual_spread:,.2f}", f"+${(capital * annual_spread)/365:,.2f} Daily")
    st.write("---")

    # 2. FETCH DATA
    st.header("2. Risk vs Reward & Correlation")
    df = pd.DataFrame()
    end = datetime.date.today()
    start = end - datetime.timedelta(days=years*365)

    with st.spinner("Fetching market data..."):
        for t in tickers:
            data = yf.download(t, start=start, end=end, progress=False)
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    df[t] = data['Close'].iloc[:, 0]
                else:
                    df[t] = data['Close']

    returns = df.pct_change().dropna()

    # CORRELATION HEATMAP
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Correlation (Crash Risk)")
        fig, ax = plt.subplots()
        sns.heatmap(returns.corr(), annot=True, cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
        st.pyplot(fig)

    # RISK VS REWARD SCATTER
    with col_b:
        st.subheader("Spot Price Volatility")
        ann_return = returns.mean() * 252 * 100
        ann_risk = returns.std() * np.sqrt(252) * 100

        fig2, ax2 = plt.subplots()
        ax2.scatter(ann_risk, ann_return, color='blue')
        for i, txt in enumerate(ann_return.index):
            ax2.annotate(txt, (ann_risk[i], ann_return[i]), xytext=(5,5), textcoords='offset points')

        ax2.set_xlabel("Risk (Annual Volatility %)")
        ax2.set_ylabel("Reward (Annual Spot Return %)")
        ax2.axhline(0, color='black', lw=1)
        # The red line shows where spot price drops wipe out your interest gain
        ax2.axhline(-annual_spread*100, color='red', ls='--', label='Interest Erased (Breakeven)')
        ax2.legend()
        st.pyplot(fig2)
