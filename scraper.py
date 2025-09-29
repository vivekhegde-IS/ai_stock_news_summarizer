import streamlit as st
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from config import POLYGON_API_KEY, GEMINI_API_KEY

# --- Helper Functions (Our existing scrapers) ---

# This is a powerful Streamlit feature that caches the output of our functions.
# It prevents re-running a function if we use the same ticker again,
# which saves a lot of time and API calls.
@st.cache_data
def scrape_tradingview(ticker):
    """Scrapes news headlines and returns them as a list."""
    st.write(f"Scraping TradingView for {ticker}...")
    headlines_list = []
    driver_path = './chromedriver.exe'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    url = f'https://in.tradingview.com/symbols/NYSE-{ticker}/news/'
    try:
        driver.get(url)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        headlines = soup.select('a[href^="/news/"]')
        for headline in headlines:
            if headline.text.strip():
                headlines_list.append(headline.text.strip())
    except Exception as e:
        st.error(f"An error occurred while scraping TradingView: {e}")
    finally:
        driver.quit()
    return headlines_list

@st.cache_data
def scrape_finviz(ticker):
    """Scrapes news headlines and returns them as a list."""
    st.write(f"Scraping Finviz for {ticker}...")
    headlines_list = []
    url = f'https://finviz.com/quote.ashx?t={ticker}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        news_table = soup.find('table', id='news-table')
        if news_table:
            for row in news_table.find_all('tr'):
                headline_link = row.find('a')
                if headline_link:
                    headlines_list.append(headline_link.text.strip())
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Finviz URL: {e}")
    return headlines_list

@st.cache_data
def scrape_polygon(ticker):
    """Fetches news headlines and returns them as a list."""
    st.write(f"Scraping Polygon.io for {ticker}...")
    headlines_list = []
    url = f'https://api.polygon.io/v2/reference/news?ticker={ticker}&limit=20&apiKey={POLYGON_API_KEY}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for article in data.get('results', []):
            headlines_list.append(article.get('title'))
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching Polygon URL: {e}")
    return headlines_list

@st.cache_data
def get_ai_summary(all_headlines, ticker):
    """Sends headlines to Gemini and returns an AI-generated summary."""
    st.write("Asking Gemini for an AI Summary...")
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    unique_headlines = list(set(all_headlines))
    headlines_text = "\n".join(unique_headlines)
    prompt = f"""
    Analyze the following news headlines for the stock ticker {ticker}.
    Based on content quality and credibility, select the top 5-7 most financially relevant and impactful headlines.
    Then, generate a concise summary (less than 500 words) of these key headlines.
    Structure the summary with a section called "What Changed Today".
    This section should synthesize the news and explain its potential impact on the stock.

    Here are the headlines:
    {headlines_text}
    """
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()
        summary = result['candidates'][0]['content']['parts'][0]['text']
        return summary
    except Exception as e:
        error_message = f"An error occurred with the AI model API call: {e}"
        try:
            # Try to get more detailed error from API response
            error_details = response.json()
            error_message += f"\nDetails: {error_details.get('error', {}).get('message', 'No details')}"
        except:
            pass # Ignore if response is not valid JSON
        st.error(error_message)
        return None


# --- Streamlit App UI ---

st.set_page_config(layout="wide", page_title="AI Stock News Summarizer")

st.title("📈 AI Stock News Summarizer")

# --- Sidebar for Ticker Input ---
with st.sidebar:
    st.header("Stock Ticker")
    ticker = st.text_input("Enter a stock ticker (e.g., AAPL, MSFT, UPS):", "UPS").upper()
    
    analyze_button = st.button("Analyze News")

# --- Main Content Area ---

if analyze_button:
    if not ticker:
        st.warning("Please enter a stock ticker.")
    else:
        st.header(f"Daily Summary for {ticker}")
        
        with st.spinner(f"Gathering news and generating summary for {ticker}..."):
            # 1. Collect all headlines
            all_headlines = []
            all_headlines.extend(scrape_tradingview(ticker))
            all_headlines.extend(scrape_finviz(ticker))
            all_headlines.extend(scrape_polygon(ticker))
            
            # 2. Get the AI summary
            if all_headlines:
                summary = get_ai_summary(all_headlines, ticker)
                if summary:
                    st.markdown(summary)
                    
                with st.expander("View Raw Headlines Collected"):
                    st.json(list(set(all_headlines)))
            else:
                st.warning("No headlines found for this ticker.")