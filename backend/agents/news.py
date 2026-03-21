import httpx
from bs4 import BeautifulSoup
import asyncio
from typing import List, Dict
import urllib.parse
import re
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class NewsSearchAgent:
    """
    Search for REAL mentions in local and global news.
    Uses DuckDuckGo + Google News RSS, with optional Gemini summarization.
    """
    
    @staticmethod
    async def search_news(query: str, callback) -> List[Dict]:
        """
        Multi-source news search pipeline.
        """
        results = []
        
        # Source 1: DuckDuckGo (Paraguayan news sites)
        ddg_results = await NewsSearchAgent._search_duckduckgo(query, callback)
        results.extend(ddg_results)
        
        # Source 2: Google News RSS
        gn_results = await NewsSearchAgent._search_google_news_rss(query, callback)
        results.extend(gn_results)
        
        # Deduplicate by title similarity
        seen_titles = set()
        unique_results = []
        for r in results:
            title_key = r["title"][:50].lower()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_results.append(r)
        
        # Gemini summarization for the batch
        if unique_results:
            unique_results = await NewsSearchAgent._summarize_with_gemini(unique_results, query, callback)
        
        return unique_results

    @staticmethod
    async def _search_duckduckgo(query: str, callback) -> List[Dict]:
        """DuckDuckGo scraping focused on Paraguayan news."""
        results = []
        sites = ["abc.com.py", "ultimahora.com", "hoy.com.py", "lanacion.com.py", "5dias.com.py"]
        search_query = f'"{query}" (' + " OR ".join([f"site:{s}" for s in sites]) + ")"
        encoded_query = urllib.parse.quote(search_query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            async with httpx.AsyncClient(timeout=15, verify=True) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    entries = soup.find_all('div', class_='result')
                    
                    if not entries:
                        callback(f"[NEWS] DuckDuckGo: sin resultados directos para '{query}'")
                        return []

                    for entry in entries[:10]:  # Cap at 10
                        title_tag = entry.find('a', class_='result__a')
                        snippet_tag = entry.find('a', class_='result__snippet')
                        if title_tag:
                            title = title_tag.get_text().strip()
                            link = title_tag['href']
                            if "uddg=" in link:
                                link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
                            
                            snippet = snippet_tag.get_text().strip() if snippet_tag else ""
                            
                            if any(site in link for site in sites):
                                results.append({
                                    "title": title,
                                    "link": link,
                                    "snippet": snippet,
                                    "date": "Reciente",
                                    "source": "DuckDuckGo"
                                })
                                callback(f"[NEWS] Hallazgo en prensa: {title[:60]}...")
                else:
                    callback(f"[NEWS] DuckDuckGo no disponible (HTTP {response.status_code})")
                    
        except Exception as e:
            callback(f"[NEWS ERROR DDG] {str(e)}")
            
        return results

    @staticmethod
    async def _search_google_news_rss(query: str, callback) -> List[Dict]:
        """Google News RSS feed search."""
        results = []
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}+Paraguay&hl=es-419&gl=PY&ceid=PY:es-419"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            async with httpx.AsyncClient(timeout=15, verify=True) as client:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'xml')
                    items = soup.find_all('item')
                    
                    for item in items[:8]:  # Cap at 8
                        title = item.find('title').get_text().strip() if item.find('title') else ""
                        link = item.find('link').get_text().strip() if item.find('link') else ""
                        pub_date = item.find('pubDate').get_text().strip() if item.find('pubDate') else "Reciente"
                        source_tag = item.find('source')
                        source_name = source_tag.get_text().strip() if source_tag else "Google News"
                        
                        if title and link:
                            results.append({
                                "title": title,
                                "link": link,
                                "date": pub_date[:16] if len(pub_date) > 16 else pub_date,
                                "snippet": "",
                                "source": source_name
                            })
                            callback(f"[NEWS RSS] {source_name}: {title[:60]}...")
                else:
                    callback(f"[NEWS RSS] Google News RSS no disponible (HTTP {response.status_code})")
        except Exception as e:
            callback(f"[NEWS ERROR RSS] {str(e)}")
        
        return results

    @staticmethod
    async def _summarize_with_gemini(articles: List[Dict], query: str, callback) -> List[Dict]:
        """Use Gemini to generate a brief summary for the news batch."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or not articles:
            return articles
        
        try:
            client = genai.Client(api_key=api_key)
            
            articles_text = "\n".join([
                f"- {a['title']} (Fuente: {a.get('source', 'N/A')})"
                for a in articles[:10]
            ])
            
            prompt = f"""Analiza estas noticias relacionadas con '{query}' (Paraguay).
Para cada noticia, genera una etiqueta de relevancia: ALTA, MEDIA, o BAJA.
Responde SOLAMENTE con un JSON array como:
[{{"index": 0, "relevancia": "ALTA", "resumen": "resumen en 15 palabras"}}]

NOTICIAS:
{articles_text}

JSON:"""
            
            def do_genai():
                return client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt
                )
            
            response = await asyncio.to_thread(do_genai)
            text = response.text.strip()
            
            # Try to parse the JSON from the response
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            if json_match:
                import json
                summaries = json.loads(json_match.group(0))
                for s in summaries:
                    idx = s.get("index", -1)
                    if 0 <= idx < len(articles):
                        articles[idx]["relevancia"] = s.get("relevancia", "MEDIA")
                        articles[idx]["ai_summary"] = s.get("resumen", "")
                callback(f"[AI NEWS] Relevancia calculada para {len(summaries)} artículos")
            
        except Exception as e:
            callback(f"[AI NEWS ERROR] {str(e)}")
        
        return articles
