import streamlit as st
import time
import requests
import json
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
POLYGON_API_KEY = st.secrets["POLYGON_API_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# --- Helper Functions ---

@st.cache_data
def scrape_tradingview(ticker):
    """Scrapes news headlines from TradingView for a given ticker."""
    st.write(f"Scraping TradingView for {ticker}...")
    headlines_list = []
    options = webdriver.ChromeOptions()
    options.add_argument("--headless"); options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage"); options.add_argument("--disable-gpu")
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    url = f'https://in.tradingview.com/symbols/AMEX-{ticker}/news/' if ticker == "SPY" else f'https://in.tradingview.com/symbols/NYSE-{ticker}/news/'
    try:
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        headlines = soup.select('a[href^="/news/"]')
        for hl in headlines:
            if hl.text.strip(): headlines_list.append(hl.text.strip())
    except Exception as e:
        st.error(f"Error scraping TradingView: {e}")
    finally:
        driver.quit()
    return headlines_list

@st.cache_data
def scrape_finviz(ticker):
    """Scrapes news headlines from Finviz for the current day only."""
    st.write(f"Scraping Finviz for {ticker}...")
    headlines_list = []
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    ]
    headers = {'User-Agent': random.choice(user_agents)}
    today_str = datetime.now().strftime('%b-%d-%y')
    url = f'https://finviz.com/quote.ashx?t={ticker}'
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        news_table = soup.find('table', id='news-table')
        if news_table:
            for row in news_table.find_all('tr'):
                date_cell = row.find('td')
                if date_cell and date_cell.text.split(' ')[0] == today_str:
                    hl_link = row.find('a')
                    if hl_link: headlines_list.append(hl_link.text.strip())
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Finviz: {e}")
    return headlines_list

@st.cache_data
def scrape_polygon(ticker):
    """Fetches news headlines from Polygon.io for a given ticker."""
    st.write(f"Scraping Polygon.io for {ticker}...")
    headlines_list = []
    url = f'https://api.polygon.io/v2/reference/news?ticker={ticker}&limit=20&apiKey={POLYGON_API_KEY}'
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
        response.raise_for_status()
        data = response.json()
        for article in data.get('results', []):
            headlines_list.append(article.get('title'))
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Polygon: {e}")
    return headlines_list

@st.cache_data
def get_ai_summary(all_headlines, ticker):
    """Sends headlines to Gemini and returns an AI-generated summary."""
    st.write("Asking Gemini for an AI Summary...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-thinking-exp:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    unique_headlines = list(set(all_headlines))
    headlines_text = "\n".join(unique_headlines)
    prompt_subject = "the overall stock market (based on S&P 500 news)" if ticker == "SPY" else f"the stock ticker {ticker}"
    prompt = f"""
    Analyze the following news headlines for {prompt_subject}.
    **Step 1:** From the headlines provided, list the top 5 most impactful headlines under a title "**Key Headlines Analyzed:**".
    **Step 2:** Based ONLY on those headlines, generate a concise summary under a title "**What Changed Today:**".
    Here are all the headlines:
    {headlines_text}
    """
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        st.error(f"Error with AI model: {e}\nResponse: {response.text}")
        return None

# --- Main App Logic ---
def run_analysis(ticker):
    """Gathers all data for a ticker and returns the summary."""
    all_headlines = []
    all_headlines.extend(scrape_tradingview(ticker))
    all_headlines.extend(scrape_finviz(ticker))
    if ticker != "SPY": # Skip Polygon for indexes
        all_headlines.extend(scrape_polygon(ticker))
    if all_headlines:
        return get_ai_summary(all_headlines, ticker)
    else:
        st.warning(f"No recent news found for {ticker}.")
        return None

# --- Streamlit App UI ---
st.set_page_config(layout="wide", page_title="AI Stock News Summarizer")
st.title("📈 AI Stock News Summarizer")

if 'summary' not in st.session_state:
    st.session_state.summary = None
if 'last_ticker' not in st.session_state:
    st.session_state.last_ticker = None

with st.sidebar:
    st.header("Stock Ticker")
    ticker_input = st.text_input("Enter a US stock ticker (e.g., AAPL, MSFT):", "UPS").upper()
    analyze_button = st.button("Analyze News")

if analyze_button and ticker_input:
    st.session_state.last_ticker = ticker_input
    st.session_state.summary = run_analysis(ticker_input)

# On first load, generate the default market overview
if st.session_state.summary is None and st.session_state.last_ticker is None:
    st.session_state.last_ticker = "SPY"
    st.session_state.summary = run_analysis("SPY")

display_ticker = st.session_state.last_ticker or "Market"
st.header(f"Daily Summary for {display_ticker}")

if st.session_state.summary:
    st.markdown(st.session_state.summary)