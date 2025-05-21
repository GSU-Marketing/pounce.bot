
import requests
from bs4 import BeautifulSoup

def scrape_program_page(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content = soup.find('main') or soup.find('div', class_='entry-content') or soup.body
        text = content.get_text(separator='\n', strip=True) if content else ''
        return text
    except Exception as e:
        return f"[ERROR] Failed to scrape {url}: {str(e)}"
