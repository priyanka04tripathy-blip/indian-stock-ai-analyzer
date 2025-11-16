import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from groq import Groq
import plotly.graph_objs as go
from datetime import datetime, timedelta
import time
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Indian Stock Name to Symbol Mapping
INDIAN_STOCKS = {
    # Major Indian Companies
    "reliance": "RELIANCE.NS", "reliance industries": "RELIANCE.NS", "ril": "RELIANCE.NS",
    "tcs": "TCS.NS", "tata consultancy": "TCS.NS", "tata consultancy services": "TCS.NS",
    "hdfc bank": "HDFCBANK.NS", "hdfc": "HDFCBANK.NS",
    "infosys": "INFY.NS",
    "icici bank": "ICICIBANK.NS", "icici": "ICICIBANK.NS",
    "hul": "HINDUNILVR.NS", "hindustan unilever": "HINDUNILVR.NS",
    "sbi": "SBIN.NS", "state bank of india": "SBIN.NS",
    "bharti airtel": "BHARTIARTL.NS", "airtel": "BHARTIARTL.NS",
    "bajaj finance": "BAJFINANCE.NS", "bajaj": "BAJFINANCE.NS",
    "lt": "LT.NS", "larsen toubro": "LT.NS", "larsen": "LT.NS",
    "itc": "ITC.NS",
    "axis bank": "AXISBANK.NS", "axis": "AXISBANK.NS",
    "asian paints": "ASIANPAINT.NS",
    "maruti": "MARUTI.NS", "maruti suzuki": "MARUTI.NS",
    "wipro": "WIPRO.NS",
    "ultra tech": "ULTRACEMCO.NS", "ultratech cement": "ULTRACEMCO.NS",
    "nestle": "NESTLEIND.NS", "nestle india": "NESTLEIND.NS",
    "titan": "TITAN.NS",
    "sun pharma": "SUNPHARMA.NS", "sun pharmaceutical": "SUNPHARMA.NS",
    "hindalco": "HINDALCO.NS",
    "jsw steel": "JSWSTEEL.NS",
    "tata steel": "TATASTEEL.NS",
    "adani ports": "ADANIPORTS.NS", "adani": "ADANIPORTS.NS",
    "power grid": "POWERGRID.NS",
    "ntpc": "NTPC.NS",
    "coal india": "COALINDIA.NS",
    "ongc": "ONGC.NS", "oil and natural gas": "ONGC.NS",
    "indian oil": "IOC.NS", "ioc": "IOC.NS",
    "gail": "GAIL.NS",
    "vedanta": "VEDL.NS",
    "jindal steel": "JINDALSTEL.NS",
    "tata motors": "TATAMOTORS.NS",
    "mahindra": "M&M.NS", "mahindra and mahindra": "M&M.NS",
    "eicher motors": "EICHERMOT.NS", "royal enfield": "EICHERMOT.NS",
    "hero motocorp": "HEROMOTOCO.NS", "hero": "HEROMOTOCO.NS",
    "bajaj auto": "BAJAJ-AUTO.NS",
    "dr reddy": "DRREDDY.NS", "dr reddys": "DRREDDY.NS",
    "cipla": "CIPLA.NS",
    "lupin": "LUPIN.NS",
    "divis labs": "DIVISLAB.NS",
    "zomato": "ZOMATO.NS",
    "paytm": "PAYTM.NS",
    "nykaa": "NYKAA.NS",
    "policybazaar": "PBFintech.NS",
    "delhivery": "DELHIVERY.NS",
}

# Page config with better styling
st.set_page_config(
    page_title="Indian Stock AI Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 100%);
    }
    .stMetric {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d44 100%);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(124, 92, 255, 0.3);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stMetric label {
        color: #b0b0b0 !important;
        font-size: 0.9rem !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #7C5CFF !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 600;
    }
    .stock-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #2d2d44 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(124, 92, 255, 0.3);
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    .info-box {
        background: rgba(124, 92, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #7C5CFF;
        margin: 10px 0;
    }
    .positive {
        color: #00ff88 !important;
    }
    .negative {
        color: #ff4444 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1e1e1e;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #b0b0b0;
    }
    .stTabs [aria-selected="true"] {
        color: #7C5CFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

def normalize_stock_name(name):
    """Normalize and find stock symbol from name"""
    if not name:
        return None
    
    name_lower = name.lower().strip()
    
    # Check if it's already a symbol (contains .NS or .BO)
    if '.NS' in name.upper() or '.BO' in name.upper():
        return name.upper()
    
    # Direct match
    if name_lower in INDIAN_STOCKS:
        return INDIAN_STOCKS[name_lower]
    
    # Partial match
    for key, symbol in INDIAN_STOCKS.items():
        if name_lower in key or key in name_lower:
            return symbol
    
    # Try with Serper to find the symbol
    return None

def search_stock_symbol(query):
    """Search for stock symbol using Serper API"""
    try:
        url = "https://google.serper.dev/search"
        payload = {
            "q": f"{query} stock symbol NSE BSE India",
            "num": 5
        }
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            results = response.json().get("organic", [])
            # Try to extract symbol from results
            for result in results:
                title = result.get("title", "").upper()
                snippet = result.get("snippet", "").upper()
                # Look for .NS pattern
                if ".NS" in title or ".NS" in snippet:
                    match = re.search(r'([A-Z]+\.NS)', title + " " + snippet)
                    if match:
                        return match.group(1)
        return None
    except:
        return None

def get_stock_data(symbol, period="5d", interval="1h"):
    """Fetch real-time stock data using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        info = ticker.info
        return data, info
    except Exception as e:
        return None, None

def get_comprehensive_stock_info(symbol, company_name):
    """Get comprehensive stock information from Serper"""
    try:
        results = {}
        
        # Search for general information
        url = "https://google.serper.dev/search"
        queries = [
            f"{company_name} {symbol} stock analysis India",
            f"{company_name} financial results earnings India",
            f"{company_name} stock price target India",
            f"{company_name} news latest India"
        ]
        
        all_news = []
        all_info = []
        
        for query in queries:
            payload = {"q": query, "num": 10}
            headers = {
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json"
            }
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                all_news.extend(data.get("news", []))
                all_info.extend(data.get("organic", []))
        
        # Get news separately
        news_url = "https://google.serper.dev/news"
        news_payload = {
            "q": f"{company_name} {symbol} stock news India",
            "num": 20
        }
        news_response = requests.post(news_url, json=news_payload, headers={
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        })
        if news_response.status_code == 200:
            all_news.extend(news_response.json().get("news", []))
        
        return {
            "news": all_news[:30],  # Limit to 30 most recent
            "search_results": all_info[:20],
            "company_name": company_name
        }
    except Exception as e:
        return {"news": [], "search_results": [], "company_name": company_name}

def get_ai_analysis(symbol, stock_data, stock_info, serper_data):
    """Get AI-powered comprehensive analysis using Groq"""
    try:
        # Prepare data summary
        if stock_data is not None and not stock_data.empty:
            current_price = stock_data['Close'].iloc[-1]
            prev_close = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
            change = current_price - prev_close
            change_pct = (change / prev_close) * 100 if prev_close > 0 else 0
            
            high_52w = stock_data['High'].max() if len(stock_data) > 0 else current_price
            low_52w = stock_data['Low'].min() if len(stock_data) > 0 else current_price
            
            # Calculate technical indicators
            sma_20 = stock_data['Close'].tail(20).mean() if len(stock_data) >= 20 else current_price
            sma_50 = stock_data['Close'].tail(50).mean() if len(stock_data) >= 50 else current_price
            
            volume = stock_data['Volume'].iloc[-1]
            avg_volume = stock_data['Volume'].tail(20).mean() if len(stock_data) >= 20 else volume
        else:
            current_price = stock_info.get('currentPrice', stock_info.get('regularMarketPrice', 0))
            prev_close = stock_info.get('previousClose', current_price)
            change = current_price - prev_close
            change_pct = ((change / prev_close) * 100) if prev_close > 0 else 0
            high_52w = stock_info.get('fiftyTwoWeekHigh', current_price)
            low_52w = stock_info.get('fiftyTwoWeekLow', current_price)
            sma_20 = current_price
            sma_50 = current_price
            volume = stock_info.get('volume', 0)
            avg_volume = stock_info.get('averageVolume', volume)
        
        # Prepare news and info summary
        news_summary = ""
        if serper_data.get("news"):
            news_summary = "\n".join([
                f"- {item.get('title', '')}: {item.get('snippet', '')[:100]}"
                for item in serper_data["news"][:10]
            ])
        
        info_summary = ""
        if serper_data.get("search_results"):
            info_summary = "\n".join([
                f"- {item.get('title', '')}: {item.get('snippet', '')[:100]}"
                for item in serper_data["search_results"][:5]
            ])
        
        company_name = serper_data.get("company_name", symbol)
        
        prompt = f"""Analyze the Indian stock {symbol} ({company_name}) with the following comprehensive information:

PRICE DATA:
Current Price: ₹{current_price:.2f}
Previous Close: ₹{prev_close:.2f}
Change: ₹{change:.2f} ({change_pct:+.2f}%)
52 Week High: ₹{high_52w:.2f}
52 Week Low: ₹{low_52w:.2f}
SMA 20: ₹{sma_20:.2f}
SMA 50: ₹{sma_50:.2f}
Volume: {volume:,.0f}
Average Volume (20d): {avg_volume:,.0f}

COMPANY INFORMATION:
- Sector: {stock_info.get('sector', 'N/A')}
- Industry: {stock_info.get('industry', 'N/A')}
- Market Cap: ₹{stock_info.get('marketCap', 0)/1e7:.2f} Cr
- P/E Ratio: {stock_info.get('trailingPE', 'N/A')}
- Book Value: ₹{stock_info.get('bookValue', 'N/A')}
- Dividend Yield: {stock_info.get('dividendYield', 0)*100 if stock_info.get('dividendYield') else 0:.2f}%
- Beta: {stock_info.get('beta', 'N/A')}

RECENT NEWS & INFORMATION:
{news_summary if news_summary else 'No recent news available'}

MARKET INTELLIGENCE:
{info_summary if info_summary else 'No additional information available'}

Provide a comprehensive analysis including:
1. **Executive Summary** - Brief overview of the stock
2. **Technical Analysis** - Price action, support/resistance, indicators
3. **Fundamental Analysis** - Financial health, valuation metrics
4. **Market Sentiment** - Based on news and market data
5. **Trading Recommendation** - Buy/Hold/Sell with reasoning
6. **Price Targets** - Short-term and medium-term targets
7. **Risk Assessment** - Key risks and concerns
8. **Investment Strategy** - Best approach for this stock

Format the analysis clearly with sections and actionable insights. Focus on Indian market context."""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Indian stock market analyst with deep knowledge of NSE, BSE, technical analysis, fundamental analysis, and Indian market trends. Provide detailed, actionable insights."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=2000
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error generating AI analysis: {str(e)}"

def get_best_indian_stocks_today():
    """Get AI recommendation for best Indian stocks for today"""
    try:
        popular_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
                          "BHARTIARTL.NS", "SBIN.NS", "BAJFINANCE.NS", "LT.NS", "ITC.NS"]
        
        prompt = f"""Based on current Indian market conditions (NSE/BSE), analyze these popular stocks: {', '.join(popular_symbols)}

Provide your top 5 best Indian stock picks for today with:
1. Stock symbol and company name
2. Current price range
3. Brief reason (2-3 sentences)
4. Expected price movement direction (Up/Down/Sideways)
5. Risk level (Low/Medium/High)
6. Entry strategy

Format as a numbered list with clear sections."""

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert Indian stock market analyst. Provide actionable stock recommendations based on NSE/BSE market analysis."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=1000
        )
        
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

def create_advanced_chart(data, symbol):
    """Create advanced interactive price chart"""
    if data is None or data.empty:
        return None
    
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name=symbol,
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444'
    ))
    
    # Add moving averages
    if len(data) >= 20:
        data['SMA20'] = data['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA20'],
            name='SMA 20',
            line=dict(color='#ffaa00', width=2)
        ))
    
    if len(data) >= 50:
        data['SMA50'] = data['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['SMA50'],
            name='SMA 50',
            line=dict(color='#7C5CFF', width=2)
        ))
    
    # Volume bars
    colors = ['#00ff88' if data['Close'].iloc[i] >= data['Open'].iloc[i] else '#ff4444' 
              for i in range(len(data))]
    
    fig.add_trace(go.Bar(
        x=data.index,
        y=data['Volume'],
        name='Volume',
        marker_color=colors,
        opacity=0.3,
        yaxis='y2'
    ))
    
    fig.update_layout(
        title=f"{symbol} - Advanced Stock Analysis",
        xaxis_title="Time",
        yaxis_title="Price (₹)",
        yaxis2=dict(title="Volume", overlaying="y", side="right"),
        template="plotly_dark",
        height=600,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

# Main App
st.title("🇮🇳 Indian Stock AI Analyzer")
st.markdown("### Powered by AI • Real-time Analysis • Comprehensive Insights")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🔍 Stock Search")
    st.markdown("**Enter stock name or symbol**")
    st.markdown("*Examples: Reliance, TCS, HDFC Bank, Infosys*")
    
    user_input = st.text_input(
        "Search Stock",
        value="",
        placeholder="Type company name (e.g., Reliance Industries)",
        key="stock_search"
    )
    
    st.markdown("---")
    
    if st.button("🏆 Get Best Indian Stocks Today", use_container_width=True):
        st.session_state.show_best_stocks = True
        st.session_state.current_symbol = None
    else:
        if 'show_best_stocks' not in st.session_state:
            st.session_state.show_best_stocks = False
    
    st.markdown("---")
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Type company names (not just symbols)
    - AI will auto-correct and find the stock
    - Get comprehensive analysis
    - View real-time charts
    - Read latest news
    """)

# Process stock search
symbol = None
company_name = ""
if user_input:
    # Try to find symbol
    symbol = normalize_stock_name(user_input)
    
    if not symbol:
        # Try Serper search
        with st.spinner("🔍 Searching for stock symbol..."):
            symbol = search_stock_symbol(user_input)
    
    if symbol:
        st.session_state.current_symbol = symbol
        st.session_state.show_best_stocks = False
        # Extract company name from input
        company_name = user_input.title()
    else:
        st.warning(f"⚠️ Could not find stock for '{user_input}'. Please try a different name or use the symbol format (e.g., RELIANCE.NS)")

# Best Stocks Section
if st.session_state.get('show_best_stocks', False):
    st.header("🏆 Best Indian Stocks for Today")
    with st.spinner("🤖 AI is analyzing market conditions..."):
        recommendations = get_best_indian_stocks_today()
        st.markdown(recommendations)
    st.markdown("---")

# Stock Analysis Section
if st.session_state.get('current_symbol'):
    symbol = st.session_state.current_symbol
    
    with st.spinner(f"📊 Fetching comprehensive data for {symbol}..."):
        # Get stock data
        stock_data, stock_info = get_stock_data(symbol, period="1mo", interval="1d")
        
        # Get comprehensive Serper data
        serper_data = get_comprehensive_stock_info(symbol, company_name or stock_info.get('longName', symbol))
    
    if stock_data is not None and stock_info:
        # Header with stock name
        company_display = stock_info.get('longName', company_name or symbol)
        st.header(f"📈 {company_display} ({symbol})")
        
        # Key Metrics Row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        current_price = stock_data['Close'].iloc[-1] if not stock_data.empty else stock_info.get('currentPrice', stock_info.get('regularMarketPrice', 0))
        prev_close = stock_info.get('previousClose', current_price)
        change = current_price - prev_close
        change_pct = ((change / prev_close) * 100) if prev_close > 0 else 0
        change_color = "positive" if change >= 0 else "negative"
        
        with col1:
            st.metric("Current Price", f"₹{current_price:.2f}")
        with col2:
            st.metric("Change", f"₹{change:.2f}", f"{change_pct:+.2f}%")
        with col3:
            market_cap = stock_info.get('marketCap', 0)
            st.metric("Market Cap", f"₹{market_cap/1e7:.2f} Cr" if market_cap > 0 else "N/A")
        with col4:
            pe_ratio = stock_info.get('trailingPE', 'N/A')
            st.metric("P/E Ratio", f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else "N/A")
        with col5:
            high_52w = stock_info.get('fiftyTwoWeekHigh', current_price)
            low_52w = stock_info.get('fiftyTwoWeekLow', current_price)
            st.metric("52W Range", f"₹{low_52w:.2f} - ₹{high_52w:.2f}")
        
        st.markdown("---")
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Advanced Chart", "🤖 AI Analysis", "📰 Latest News", "📈 Market Data", "ℹ️ Company Info"])
        
        with tab1:
            st.subheader("📊 Advanced Price Chart with Technical Indicators")
            if not stock_data.empty:
                fig = create_advanced_chart(stock_data, symbol)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                
                # Additional technical metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    sma_20 = stock_data['Close'].tail(20).mean() if len(stock_data) >= 20 else current_price
                    st.metric("SMA 20", f"₹{sma_20:.2f}")
                with col2:
                    sma_50 = stock_data['Close'].tail(50).mean() if len(stock_data) >= 50 else current_price
                    st.metric("SMA 50", f"₹{sma_50:.2f}")
                with col3:
                    volume = stock_data['Volume'].iloc[-1] if not stock_data.empty else 0
                    st.metric("Volume", f"{volume:,.0f}")
                with col4:
                    volatility = stock_data['Close'].pct_change().std() * 100 if len(stock_data) > 1 else 0
                    st.metric("Volatility", f"{volatility:.2f}%")
            else:
                st.info("Chart data loading...")
        
        with tab2:
            st.subheader("🤖 AI-Powered Comprehensive Analysis")
            with st.spinner("🤖 AI is analyzing the stock..."):
                analysis = get_ai_analysis(symbol, stock_data, stock_info, serper_data)
                st.markdown(analysis)
        
        with tab3:
            st.subheader("📰 Latest News & Market Updates")
            news_items = serper_data.get("news", [])
            if news_items:
                for i, item in enumerate(news_items[:15]):
                    with st.container():
                        st.markdown(f"### {item.get('title', 'No title')}")
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**Source:** {item.get('source', 'Unknown')}")
                            st.markdown(f"{item.get('snippet', 'No description available')}")
                        with col2:
                            if item.get('link'):
                                st.markdown(f"[🔗 Read Full Article]({item.get('link')})")
                        if i < len(news_items) - 1:
                            st.markdown("---")
            else:
                st.info("No recent news available for this stock.")
        
        with tab4:
            st.subheader("📈 Detailed Market Data")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Price Metrics")
                metrics_data = {
                    "Current Price": f"₹{current_price:.2f}",
                    "Previous Close": f"₹{prev_close:.2f}",
                    "Open": f"₹{stock_info.get('open', 'N/A')}",
                    "Day High": f"₹{stock_info.get('dayHigh', 'N/A')}",
                    "Day Low": f"₹{stock_info.get('dayLow', 'N/A')}",
                    "52 Week High": f"₹{high_52w:.2f}",
                    "52 Week Low": f"₹{low_52w:.2f}",
                }
                for key, value in metrics_data.items():
                    st.markdown(f"**{key}:** {value}")
            
            with col2:
                st.markdown("### Financial Metrics")
                financial_data = {
                    "Market Cap": f"₹{market_cap/1e7:.2f} Cr" if market_cap > 0 else "N/A",
                    "P/E Ratio": f"{stock_info.get('trailingPE', 'N/A')}",
                    "P/B Ratio": f"{stock_info.get('priceToBook', 'N/A')}",
                    "Dividend Yield": f"{stock_info.get('dividendYield', 0)*100 if stock_info.get('dividendYield') else 0:.2f}%",
                    "Beta": f"{stock_info.get('beta', 'N/A')}",
                    "EPS": f"₹{stock_info.get('trailingEps', 'N/A')}",
                    "Book Value": f"₹{stock_info.get('bookValue', 'N/A')}",
                }
                for key, value in financial_data.items():
                    st.markdown(f"**{key}:** {value}")
        
        with tab5:
            st.subheader("ℹ️ Company Information")
            info_cols = {
                "Company Name": stock_info.get('longName', 'N/A'),
                "Sector": stock_info.get('sector', 'N/A'),
                "Industry": stock_info.get('industry', 'N/A'),
                "Website": stock_info.get('website', 'N/A'),
                "Employees": f"{stock_info.get('fullTimeEmployees', 'N/A'):,}" if isinstance(stock_info.get('fullTimeEmployees'), int) else 'N/A',
                "Headquarters": stock_info.get('city', 'N/A') + ", " + stock_info.get('country', 'India'),
            }
            
            for key, value in info_cols.items():
                st.markdown(f"**{key}:** {value}")
            
            if stock_info.get('longBusinessSummary'):
                st.markdown("---")
                st.markdown("### Business Summary")
                st.markdown(stock_info.get('longBusinessSummary'))
    else:
        st.error(f"❌ Could not fetch data for {symbol}. Please check the symbol and try again.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #b0b0b0; padding: 20px;'>
    <p><strong>⚠️ Disclaimer:</strong> This tool is for informational purposes only. Always do your own research before making investment decisions.</p>
    <p>Powered by Groq AI • Serper API • YFinance</p>
</div>
""", unsafe_allow_html=True)
