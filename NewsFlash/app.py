from flask import Flask, render_template, redirect, url_for, request, Markup
from bs4 import BeautifulSoup
import requests
import pandas as pd  # Import pandas for Excel functionality
import time
from datetime import datetime

app = Flask(__name__)
app.static_folder = 'static'

def scrape_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (The , like Gecko) Chrome/94.0.4606.71 Safari/537.36 '
        # Add other necessary headers here if needed
    }

    proxies = {
        # Add proxies here if you have a list of rotating proxies
    }

    attempts = 0
    while attempts < 3:  # Try a maximum of 3 times
        try:
            if proxies:
                proxy = next(proxies)
                response = requests.get(url, headers=headers, proxies={'http': proxy, 'https': proxy}, timeout=10)
            else:
                response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.content
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)  # Wait for a few seconds before retrying
            attempts += 1

    return None

# for save data on excel sheet as well

def save_to_excel(news_data):
    try:
        df = pd.DataFrame(news_data)
        file_name = 'scraped_news.xlsx'
        df.to_excel(file_name, index=False)
        print(f"News data saved to {file_name}")
    except Exception as e:
        print(f"Error occurred while saving to Excel: {e}")



# ... (Your existing code)

@app.route('/')
def start():
    return render_template("start.html")

@app.route('/choice')
def choice():
    return render_template("choice.html")

@app.route('/news_page', methods=["GET", "POST"])
def index():
    category = request.args.get('category')
    
    if category == 'tech':
        url = "https://www.businesstoday.in/technology/news"
    elif category == 'stock':
        url = "https://www.businesstoday.in/markets/stocks"
    elif category == 'corporate':
        url = "https://www.businesstoday.in/impact-feature/corporate"
    elif category == 'market':
        url = "https://www.businesstoday.in/markets/global-markets"
    elif category == 'politics':
        url = "https://www.businesstoday.in/india"
    else:
        return "Invalid category"
    
    req_content = scrape_data(url)

    if req_content:
        soup = BeautifulSoup(req_content, "html.parser")
        outerdata = soup.find_all("div", class_="widget-listing", limit=6)
        
        # Extracting news data
        news_data = [{'title': data.div.div.a['title'], 'link': data.div.div.a['href']} for data in outerdata]
        
        # Modified code to include a redirect symbol at the start of each news item
        NewsResult = "\n".join(f"<a href='{data['link']}'>&#10140;</a> \u2022 {data['title']}" for data in news_data)

        # Saving news data to Excel
        save_to_excel(news_data)
        print("News data saved to Excel!")  # Debug print
        
    else:
        NewsResult = "Failed to retrieve data. Please try again later."

    return render_template("index.html", News=Markup(NewsResult))
    
if __name__ == "__main__":
    app.run(debug=True)