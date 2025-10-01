# 📈 AI Stock News Summarizer

An intelligent, cloud-deployed web application that scrapes real-time stock news from multiple financial sources and uses the Google Gemini AI model to generate concise, insightful daily summaries for any given stock ticker.

### [➡️ View the Live Demo URL Here](https://aistocknewssummarizer-mxsvlsuvyxq5yntruvhojw.streamlit.app/)


---

## The Challenge

This project was built to solve the challenge of creating a cost-effective, scalable tool for traders and investors to quickly digest daily news. The goal was to aggregate data from disparate sources, use AI to derive meaningful insights, and present them in a clean, accessible user interface, all while keeping monthly operational costs under $5.

## Key Features

- **Multi-Source Data Aggregation:** Fetches news in real-time from three distinct sources to ensure comprehensive coverage:
    - **TradingView:** Scraped using Selenium to handle dynamic JavaScript-loaded content.
    - **Finviz:** Scraped using Requests and BeautifulSoup for fast HTML parsing.
    - **Polygon.io:** Integrated via a REST API for structured, high-speed data retrieval.
- **AI-Powered Analysis:** Leverages the **Google Gemini Pro** model to analyze a large volume of headlines. The AI is prompted to:
    - Select the 5-7 most financially impactful headlines.
    - Generate a concise, human-readable summary titled "What Changed Today."
- **Interactive Web Interface:** A clean and professional UI built with **Streamlit** that allows users to:
    - View a default summary of the overall market (S&P 500) on page load.
    - Enter any US stock ticker to receive a custom, on-demand summary.
- **Cost-Effective Cloud Deployment:** Fully deployed and operational on **Streamlit Community Cloud**, with a total monthly cost of **$0**, successfully meeting the project's budget constraints.

## Technology Stack

- **Backend:** Python
- **Frontend:** Streamlit
- **Web Scraping:** Selenium, BeautifulSoup4, Requests
- **AI Model:** Google Gemini API
- **Deployment:** Streamlit Community Cloud
- **Code Hosting:** GitHub

## Local Setup and Installation

To run this project on your local machine, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a secrets file:**
    - Create a file named `config.py`.
    - Add your secret API keys to this file in the following format:
      ```python
      POLYGON_API_KEY = "YOUR_POLYGON_KEY"
      GEMINI_API_KEY = "YOUR_GEMINI_KEY"
      ```

5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## Deployment

This application is deployed on Streamlit Community Cloud. The deployment configuration includes:
- **`requirements.txt`**: Specifies the necessary Python packages.
- **`packages.txt`**: Specifies the Debian package `chromium-driver` required for Selenium to run in the cloud environment.
- **Streamlit Secrets:** The `POLYGON_API_KEY` and `GEMINI_API_KEY` are stored securely in the app's settings on Streamlit Cloud and are not exposed in the repository.

## Cost Analysis

This project was designed to be highly cost-effective, leveraging free-tier services.
- **Hosting (Streamlit Community Cloud):** $0/month
- **Code Repository (GitHub):** $0/month
- **APIs (Polygon & Gemini):** $0/month (Usage is well within the generous free tiers)
- **Total Monthly Cost: $0**