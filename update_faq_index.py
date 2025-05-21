
import json
from page_scraper import scrape_program_page

def convert_to_faq_format(text, source_url):
    entries = []
    for para in text.splitlines():
        if len(para.strip().split()) > 5:
            entries.append({"source": source_url, "answer": para.strip()})
    return entries

def update_faq_data(urls, faq_file="faq_data.json"):
    try:
        with open(faq_file, "r") as f:
            faq_data = json.load(f)
    except FileNotFoundError:
        faq_data = []

    for url in urls:
        print(f"Scraping: {url}")
        text = scrape_program_page(url)
        new_entries = convert_to_faq_format(text, url)
        faq_data.extend(new_entries)

    with open(faq_file, "w") as f:
        json.dump(faq_data, f, indent=2)

    print(f"✅ Updated {faq_file} with content from {len(urls)} URLs.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python update_faq_index.py <url1> <url2> ...")
    else:
        update_faq_data(sys.argv[1:])
