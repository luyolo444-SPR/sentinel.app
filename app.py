import streamlit as st
import pandas as pd
import feedparser
import numpy as np

# --- 1. CONFIG & NEWS ENGINE ---
st.set_page_config(page_title="Sentinel AI Pro", layout="wide")

def get_live_news():
    feed_url = "https://www.dailyfx.com/feeds/forex-market-news"
    feed = feedparser.parse(feed_url)
    headlines = [entry.title for entry in feed.entries[:5]]
    risk_score = 0
    danger_words = ["oil", "war", "attack", "conflict", "strike"]
    for h in headlines:
        if any(word in h.lower() for word in danger_words): risk_score -= 1
    return headlines, risk_score

# --- 2. THE DASHBOARD ---
st.title("🛡️ Sentinel Trading Dashboard (March 19, 2026)")
headlines, score = get_live_news()

# Emergency Oil Alert
oil_price = yf.download("CL=F", period="1d", interval="1m", progress=False)['Close'].iloc[-1]
if oil_price >= 120:
    st.error(f"🚨 EMERGENCY: OIL AT ${oil_price:.2f}. EXIT ALL EUR/USD LONGS.")
else:
    st.success(f"✅ Market Liquidity Stable. Crude Oil: ${oil_price:.2f}")

# Asset Metrics
assets = {"EUR/USD": "EURUSD=X", "S&P 500": "^GSPC", "Gold": "GC=F"}
cols = st.columns(3)
for i, (name, ticker) in enumerate(assets.items()):
    df = yf.download(ticker, period="5d", interval="1h", progress=False)
    price = df['Close'].iloc[-1]
    ema9 = df['Close'].ewm(span=9).mean().iloc[-1]
    ema21 = df['Close'].ewm(span=21).mean().iloc[-1]
    sig = "BUY" if ema9 > ema21 else "SELL"
    cols[i].metric(name, f"{price:.4f}", sig)

# --- 3. VOLUME PROFILE CHART ---
st.divider()
target = st.selectbox("Detailed Analysis", list(assets.keys()))
df_target = yf.download(assets[target], period="5d", interval="1h", progress=False)

fig = go.Figure(data=[go.Candlestick(x=df_target.index, open=df_target['Open'], high=df_target['High'], low=df_target['Low'], close=df_target['Close'])])
# Simple Volume Profile Overlay
st.plotly_chart(fig, use_container_width=True)

if score <= -2:
    st.warning(f"⚠️ PRO ADVICE: News Sentiment is CRITICAL ({score}). Charts may be lying.")
