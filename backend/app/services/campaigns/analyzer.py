import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def analyze_website(url: str) -> Dict[str, Any]:
    """Scrapes a website to extract product intelligence for campaign generation."""
    try:
        # Avoid blocking by providing a common user agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Basic metadata
        title = soup.title.string if soup.title else ""
        meta_desc = ""
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag and 'content' in desc_tag.attrs:
            meta_desc = desc_tag['content']

        # Extract headings for features/benefits
        h1s = [h.get_text(strip=True) for h in soup.find_all('h1')]
        h2s = [h.get_text(strip=True) for h in soup.find_all('h2')]
        h3s = [h.get_text(strip=True) for h in soup.find_all('h3')]

        # Extract main text content (limited to avoid token overflow)
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
        main_text = " ".join([p for p in paragraphs if len(p) > 20])[:3000]

        # Try to find CTAs
        buttons = [b.get_text(strip=True) for b in soup.find_all(['button', 'a']) if b.get_text(strip=True)]
        ctas = list(set([b for b in buttons if len(b) < 30 and any(w in b.lower() for w in ['get', 'start', 'buy', 'try', 'sign', 'join'])]))

        return {
            "title": title,
            "meta_description": meta_desc,
            "h1": h1s,
            "h2": h2s[:10], # Limit lists to prevent massive JSONs
            "main_text_snippet": main_text,
            "extracted_ctas": ctas[:10]
        }
    except Exception as e:
        logger.error(f"Failed to analyze website {url}: {e}")
        return {
            "title": "",
            "meta_description": "",
            "main_text_snippet": f"Failed to extract content: {e}",
            "h1": [],
            "h2": [],
            "extracted_ctas": []
        }
