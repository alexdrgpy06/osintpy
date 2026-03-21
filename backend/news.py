from duckduckgo_search import DDGS
import logging

logger = logging.getLogger("news_fetcher")

class NewsScraper:
    """
    Scraper para DuckDuckGo News y RSS de prensa paraguaya.
    """
    @staticmethod
    async def search_ddg_news(query: str, max_results: int = 5):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.news(query, region='es-py', safesearch='off', timelimit='m', max_results=max_results))
                return [{
                    "title": r['title'],
                    "url": r['url'],
                    "source": r['source'],
                    "date": r['date'],
                    "snippet": r['body']
                } for r in results]
        except Exception as e:
            logger.error(f"DDG News Error: {e}")
            return []

    @staticmethod
    async def get_combined_news(query: str):
        # Combina DDG News con búsquedas específicas en sitios de PY
        ddg = await NewsScraper.search_ddg_news(query)
        site_specific = []
        try:
            with DDGS() as ddgs:
                q_sites = f'"{query}" (site:abc.com.py OR site:ultimahora.com OR site:lanacion.com.py OR site:nanduti.com.py OR site:hoy.com.py OR site:extra.com.py)'
                res = list(ddgs.text(q_sites, max_results=5))
                site_specific = [{
                    "title": r['title'],
                    "url": r['href'],
                    "source": "Prensa PY",
                    "date": "N/A",
                    "snippet": r['body']
                } for r in res]
        except: pass
        
        return ddg + site_specific
