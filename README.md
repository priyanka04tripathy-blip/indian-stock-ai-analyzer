# 🇮🇳 Indian Stock AI Analyzer

A comprehensive Indian stock analysis application built with Streamlit, using Serper API for news and Groq AI (llama-3.3-70b-versatile) for technical analysis.

## Features

- 🇮🇳 **Indian Stock Focus** - Optimized for NSE/BSE stocks with 50+ pre-mapped companies
- 🔍 **Smart Search** - Type company names (e.g., "Reliance", "TCS") - AI auto-corrects to symbols
- 📈 **Real-time Stock Prices** - Get live stock data using YFinance
- 🤖 **AI-Powered Analysis** - Comprehensive 8-section analysis using Groq AI (llama-3.3-70b-versatile)
- 📰 **Latest Stock News** - Fetch up to 30 recent news articles using Serper API
- 📊 **Advanced Charts** - Interactive candlestick charts with moving averages and volume
- 🏆 **Best Indian Stocks** - AI recommendations for top picks today
- ℹ️ **Company Information** - Detailed company data, financial metrics, and business summary
- 🎨 **Beautiful UI** - Modern dark theme with gradient design

## Installation

1. Navigate to the stock folder:
```bash
cd stock
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Install dependencies (if not already installed):
```bash
pip install -r requirements.txt
```

## Running the App

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Run Streamlit:
```bash
streamlit run app.py
```

3. The app will open in your default browser at `http://localhost:8501`

## Usage

1. **Search for a Stock**: Type company name (e.g., "Reliance Industries", "TCS", "HDFC Bank") - no need for exact symbols!
2. **View Real-time Data**: See current price, change, market cap, P/E ratio, and 52-week range
3. **Check AI Analysis**: Get comprehensive 8-section analysis including technical, fundamental, sentiment, and recommendations
4. **Read News**: View up to 15 latest news articles from Serper
5. **View Advanced Charts**: Interactive candlestick charts with SMA 20/50, volume bars, and technical indicators
6. **Get Recommendations**: Click "Get Best Indian Stocks Today" for AI-powered top picks

## API Keys

The app uses the following API keys (configured in `app.py`):
- **Groq API**: For AI-powered analysis using llama-3.3-70b-versatile model
- **Serper API**: For fetching comprehensive stock news and market intelligence

**Note**: Make sure to add your own API keys in `app.py` if you're cloning this repository.

## Requirements

- Python 3.8+
- Streamlit
- YFinance
- Groq
- Requests
- Pandas
- NumPy
- Plotly

## Note

This tool is for informational purposes only. Always do your own research before making investment decisions.

