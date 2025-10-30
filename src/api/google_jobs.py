import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from config.api_config import APIConfig


class GoogleJobsAPI:
    """Simple Google crawl-based job search fallback.

    This performs a basic HTTP GET to Google search results and extracts top result
    links and snippets. It's a lightweight crawl for local testing and is not a
    replacement for an official API (results vary and scraping may be blocked).
    """
    def __init__(self):
        # Keep API config available but prefer simple crawl for searches
        self.api_key = APIConfig.GOOGLE_SEARCH_API_KEY
        self.search_engine_id = APIConfig.GOOGLE_SEARCH_ENGINE_ID

    def is_available(self) -> bool:
        # We always report available since we can crawl Google search pages
        return True

    def search_jobs(self, query: str, location: str = None, skills: List[str] = None) -> List[Dict[str, Any]]:
        """Perform a simple Google web search and parse top results as job postings."""
        search_query = f"{query} jobs"
        if location:
            search_query += f" in {location}"

        url = 'https://www.google.com/search'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/1'
                          '16.0.0.0 Safari/537.36'
        }
        params = {'q': search_query, 'num': 10}

        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code != 200:
                print(f"Google crawl search returned status: {resp.status_code}")
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')

            # Find search result blocks - Google markup varies; look for common anchors
            results = []
            for g in soup.select('div.g'):
                a = g.find('a', href=True)
                title = g.find('h3')
                snippet = g.select_one('.IsZvec') or g.select_one('.st')
                if a and title:
                    results.append({
                        'title': title.get_text(strip=True),
                        'link': a['href'],
                        'snippet': snippet.get_text(strip=True) if snippet else ''
                    })

            # Fallback: if no div.g found, try anchors under search
            if not results:
                for a in soup.select('a'):
                    href = a.get('href')
                    txt = a.get_text(strip=True)
                    if href and txt and href.startswith('http') and len(txt) > 20:
                        results.append({'title': txt, 'link': href, 'snippet': ''})

            jobs = []
            for idx, item in enumerate(results[:8]):
                job = {
                    'id': f"google_crawl_{idx}_{abs(hash(item.get('link','')))%10_000_000}",
                    'title': item.get('title', '').split(' - ')[0],
                    'company': 'See listing',
                    'location': location or 'Various',
                    'description': item.get('snippet', ''),
                    'requirements': skills or [],
                    'salary_range': 'Not specified',
                    'hr_contact': {'email': '', 'name': 'See website'},
                    'url': item.get('link', ''),
                    'source': 'google_crawl'
                }
                jobs.append(job)

            return jobs

        except Exception as e:
            print(f"Google crawl search failed: {e}")
            return []
