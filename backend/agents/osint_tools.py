import subprocess
import os
import sys
import time
import asyncio
import phonenumbers
import re
import httpx
from typing import List, Dict, Generator, Optional, Callable
from urllib.parse import urlparse, quote_plus, unquote
from bs4 import BeautifulSoup

class OSINTToolAgent:
    """
    OSINT Tool Orchestrator v4.
    Handles subprocesses for Sherlock, Maigret, Blackbird, Toutatis.
    Includes aggressive false-positive filtering and URL validation.
    """

    # ═══════════════════════════════════════════════════════════════
    # FALSE POSITIVE FILTER — URLs that tools falsely report as "found"
    # ═══════════════════════════════════════════════════════════════
    BLACKLISTED_URLS = {
        "https://discord.com",          # Discord always returns 200
        "https://www.discord.com",
        "https://open.spotify.com",     # Spotify always 200
    }
    
    BLACKLISTED_DOMAINS = [
        "hudsonrock.com",    # API endpoint, not a real profile
        "cavalier.",         # Same 
    ]
    
    BLACKLISTED_URL_PATTERNS = [
        r"/api/",            # Any API endpoint is not a profile
        r"/search/",         # Search pages (not actual profiles)
        r"search\?",         # Search query params
        r"user\.aspx\?",     # Generic user search pages (Roblox, etc.)
        r"\?username=",      # API-style lookups
        r"\?q=",             # Search queries
    ]

    # Pre-computed normalized sets and compiled regexes for O(1) matching
    _NORMALIZED_BLACKLISTED_URLS = {u.lower().rstrip("/") for u in BLACKLISTED_URLS}
    _COMPILED_BLACKLISTED_PATTERNS = [re.compile(p) for p in BLACKLISTED_URL_PATTERNS]

    # ═══════════════════════════════════════════════════════════════
    # PLATFORM NAME MAPPING — exact domain match (no substring!)
    # ═══════════════════════════════════════════════════════════════
    PLATFORM_MAP = {
        "github.com": "GitHub",
        "twitter.com": "X/Twitter",
        "x.com": "X/Twitter",
        "instagram.com": "Instagram",
        "facebook.com": "Facebook",
        "linkedin.com": "LinkedIn",
        "reddit.com": "Reddit",
        "tiktok.com": "TikTok",
        "youtube.com": "YouTube",
        "pinterest.com": "Pinterest",
        "tumblr.com": "Tumblr",
        "twitch.tv": "Twitch",
        "medium.com": "Medium",
        "dev.to": "Dev.to",
        "stackoverflow.com": "StackOverflow",
        "gitlab.com": "GitLab",
        "bitbucket.org": "Bitbucket",
        "soundcloud.com": "SoundCloud",
        "spotify.com": "Spotify",
        "open.spotify.com": "Spotify",
        "flickr.com": "Flickr",
        "vimeo.com": "Vimeo",
        "behance.net": "Behance",
        "dribbble.com": "Dribbble",
        "telegram.org": "Telegram",
        "t.me": "Telegram",
        "snapchat.com": "Snapchat",
        "mastodon.social": "Mastodon",
        "keybase.io": "Keybase",
        "threads.net": "Threads",
        "roblox.com": "Roblox",
        "audiojungle.net": "AudioJungle",
        "themeforest.net": "ThemeForest",
        "envato.com": "Envato",
        "artbreeder.com": "Artbreeder",
        "gog.com": "GOG",
        "247ctf.com": "247CTF",
        "sketchfab.com": "Sketchfab",
        "xboxgamertag.com": "Xbox",
        "pastebin.com": "Pastebin",
        "replit.com": "Replit",
        "codepen.io": "CodePen",
        "tryhackme.com": "TryHackMe",
        "hackthebox.com": "HackTheBox",
        "odysee.com": "Odysee",
        "hive.blog": "Hive",
        "rumble.com": "Rumble",
        "boardgamegeek.com": "BoardGameGeek",
        "letterboxd.com": "Letterboxd",
        "last.fm": "LastFM",
        "chess.com": "Chess.com",
        "lichess.org": "Lichess",
    }

    @classmethod
    def extract_platform_name(cls, url: str) -> str:
        """Extract clean platform name using EXACT domain matching."""
        try:
            domain = urlparse(url).netloc.lower().replace("www.", "")
            # Exact match first
            if domain in cls.PLATFORM_MAP:
                return cls.PLATFORM_MAP[domain]
            # Try parent domain (e.g. 'profile.example.com' -> 'example.com')
            parts = domain.split(".")
            if len(parts) > 2:
                parent = ".".join(parts[-2:])
                if parent in cls.PLATFORM_MAP:
                    return cls.PLATFORM_MAP[parent]
            # Fallback: capitalize first part
            return parts[0].capitalize() if parts else "Unknown"
        except:
            return "Unknown"

    @classmethod
    def is_false_positive(cls, url: str) -> bool:
        """Check if a URL is a known false positive."""
        url_lower = url.lower().rstrip("/")
        
        # Exact match blacklist (O(1) lookup using pre-computed set)
        if url_lower in cls._NORMALIZED_BLACKLISTED_URLS:
            return True
        
        # Domain blacklist
        try:
            domain = urlparse(url_lower).netloc
            for bd in cls.BLACKLISTED_DOMAINS:
                if bd in domain:
                    return True
        except:
            pass
        
        # Pattern blacklist (using pre-compiled regex patterns)
        for pattern in cls._COMPILED_BLACKLISTED_PATTERNS:
            if pattern.search(url_lower):
                return True
        
        # URL is clearly a search/query page (has the username in query params, not path)
        parsed = urlparse(url_lower)
        if parsed.query and not parsed.path.rstrip("/"):
            return True
        
        return False

    @staticmethod
    def stream_command(cmd: List[str], cwd: str, timeout: int = 60) -> Generator[str, None, None]:
        """Stream output from a subprocess."""
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        try:
            process = subprocess.Popen(
                cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="ignore", bufsize=1, env=env
            )
            start_time = time.time()
            while True:
                line = process.stdout.readline()
                if not line:
                    if process.poll() is not None: break
                    time.sleep(0.1)
                    continue
                if time.time() - start_time > timeout:
                    yield f"[SYSTEM] Timeout ({timeout}s). Terminando..."
                    process.terminate()
                    break
                yield line
            process.stdout.close()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            yield "[SYSTEM] Proceso terminado por tiempo."
        except Exception as e:
            yield f"[SYSTEM ERROR] {str(e)}"

    @classmethod
    def _extract_photo(cls, url: str) -> Optional[str]:
        """Extract profile photo from GitHub/Twitter."""
        if "github.com" in url and "%" not in url:
            username = url.rstrip("/").split("/")[-1]
            if username and len(username) > 1:
                return f"https://github.com/{username}.png"
        return None

    @classmethod
    def _extract_meta(cls, tool_name: str, line: str) -> Dict:
        """Extract extra metadata (bio, location, name, etc) from tool output lines."""
        meta = {}
        # Maigret/Social-Analyzer format support
        if tool_name in ["Maigret", "Social-Analyzer"]:
            for field in ["status", "bio", "location", "name", "description", "title"]:
                match = re.search(fr'{field}\s*:\s*([^,\]\)]+)', line, re.I)
                if match:
                    val = match.group(1).strip()
                    if val and val.lower() not in ["none", "n/a", "unknown"]:
                        fkey = "bio" if field.lower() in ("description", "title") else field.lower()
                        meta[fkey] = val
            
            if "name" in meta:
                meta["full_name"] = meta.pop("name")
        
        return meta

    @classmethod
    def run_tool_streaming(cls, tool_name: str, cmd: List[str], cwd: str, callback: Callable,
                           current_logs: List[str], consolidated_results: List[Dict], timeout: int = 60):
        """Run a CLI tool and parse results with false-positive filtering."""
        callback(f"[INFO] Iniciando {tool_name}...")
        
        last_node = None
        for line in cls.stream_command(cmd, cwd, timeout=timeout):
            clean = line.strip()
            if not clean: continue
            # Filter noise
            if any(skip in clean for skip in ["Checking for updates", "Want detailed logs", "──", "══"]):
                continue
            
            current_logs.append(f"[{tool_name}] {clean}")
            
            # Look for [+] hits (Sherlock/Maigret/Blackbird format)
            if "[+]" in clean:
                url_match = re.search(r'https?://[^\s\]\)]+', clean)
                if url_match:
                    found_url = url_match.group(0).rstrip(")")
                    
                    if cls.is_false_positive(found_url):
                        current_logs.append(f"[{tool_name}] [FILTERED] Falso positivo descartado: {found_url}")
                        callback(f"[FILTERED] Descartado: {found_url}")
                        continue
                    
                    platform = cls.extract_platform_name(found_url)
                    normalized = found_url.lower().rstrip("/")
                    
                    existing = next((n for n in consolidated_results if n.get("value", "").lower().rstrip("/") == normalized), None)
                    if not existing:
                        node = {
                            "type": "social", "source": tool_name, "value": found_url, 
                            "platform": platform, "meta": {}
                        }
                        consolidated_results.append(node)
                        last_node = node
                        callback(f"[+] {platform}: {found_url}")
                        
                        photo = cls._extract_photo(found_url)
                        if photo and not any(n.get("value") == photo for n in consolidated_results):
                            consolidated_results.append({"type": "photo", "source": "Auto-Extract", "value": photo})
                    else:
                        last_node = existing
                        callback(f"[DUP] Ya registrado: {found_url}")
            
            # Try to attach metadata to the last found node (especially for Maigret and Social-Analyzer)
            elif last_node and tool_name in ["Maigret", "Social-Analyzer"]:
                meta = cls._extract_meta(tool_name, clean)
                if meta:
                    last_node["meta"].update(meta)
                    if "bio" in meta: callback(f"[META] Bio: {meta['bio'][:50]}...")
            
            elif tool_name == "Holehe" and "[+]" in clean:
                node = {"type": "email_leak", "source": "Holehe", "value": clean}
                if node not in consolidated_results:
                    consolidated_results.append(node)
                    callback(clean)
        
        callback(f"[INFO] {tool_name} finalizado.")

    @classmethod
    def run_phone_osint(cls, phone: str, callback: Callable, consolidated_results: List[Dict]):
        callback(f"[INFO] Analizando teléfono: {phone}")
        try:
            clean_phone = "".join(filter(str.isdigit, phone))
            if not clean_phone.startswith("+"):
                if clean_phone.startswith("0"): clean_phone = "595" + clean_phone[1:]
                clean_phone = "+" + clean_phone
            parsed = phonenumbers.parse(clean_phone, None)
            if not phonenumbers.is_valid_number(parsed):
                callback("[ERROR] Número inválido")
                return
            region = phonenumbers.region_code_for_number(parsed)
            carrier_name = ""
            try:
                from phonenumbers import carrier, geocoder
                carrier_name = carrier.name_for_number(parsed, "es")
                location = geocoder.description_for_number(parsed, "es")
                callback(f"[INFO] Región: {region}, Carrier: {carrier_name or 'N/A'}, Ubicación: {location or 'N/A'}")
            except:
                callback(f"[INFO] Región: {region}")
            node = {"type": "phone_info", "source": "PhoneAnalyzer", "value": f"Valid: {phone} ({region}, {carrier_name or 'N/A'})"}
            if node not in consolidated_results: consolidated_results.append(node)
        except Exception as e:
            callback(f"[ERROR PHONE] {str(e)}")

    # ═══════════════════════════════════════════════════════════════
    # CLI Tools
    # ═══════════════════════════════════════════════════════════════

    @classmethod
    def run_sherlock_live(cls, username: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sherlock_dir = os.path.join(project_root, "sherlock")
        cmd = [sys.executable, "-m", "sherlock_project", username, "--timeout", "10", "--print-found", "--no-color"]
        return cls.run_tool_streaming("Sherlock", cmd, sherlock_dir, callback, current_logs, consolidated_results, timeout=120)

    @classmethod
    def run_maigret_live(cls, username: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        cmd = [sys.executable, "-m", "maigret", username, "--timeout", "20", "-n", "30", "--no-color"]
        return cls.run_tool_streaming("Maigret", cmd, os.getcwd(), callback, current_logs, consolidated_results, timeout=180)

    @classmethod
    def run_blackbird_live(cls, username: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        blackbird_dir = os.path.join(project_root, "blackbird")
        cmd = [sys.executable, "blackbird.py", "-u", username]
        return cls.run_tool_streaming("Blackbird", cmd, blackbird_dir, callback, current_logs, consolidated_results, timeout=120)

    @classmethod
    def run_holehe_live(cls, email: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        # Holehe exists as local dir, not pip-installed
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        holehe_dir = os.path.join(project_root, "holehe")
        
        # Try different module paths
        if os.path.exists(os.path.join(holehe_dir, "holehe", "core.py")):
            cmd = [sys.executable, "-c", f"import sys; sys.path.insert(0, r'{holehe_dir}'); from holehe.core import *; import asyncio; asyncio.run(main())"]
        else:
            cmd = [sys.executable, "-m", "holehe", email]
        
        callback(f"[INFO] Holehe: Verificando registros de email...")
        # If holehe isn't available, skip gracefully
        try:
            return cls.run_tool_streaming("Holehe", cmd, holehe_dir, callback, current_logs, consolidated_results, timeout=90)
        except Exception as e:
            callback(f"[WARN] Holehe no disponible: {str(e)}")

    @classmethod
    def run_toutatis_live(cls, username: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        cmd = [sys.executable, "-m", "toutatis", "-u", username]
        return cls.run_tool_streaming("Toutatis", cmd, os.getcwd(), callback, current_logs, consolidated_results, timeout=60)

    @classmethod
    def run_social_analyzer_live(cls, username: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        cmd = [sys.executable, "-m", "social_analyzer", "--username", username, "--websites", "all", "--metadata", "--extract"]
        callback(f"[INFO] Iniciando rastreo pasivo (+1000 sitios) con Social-Analyzer...")
        return cls.run_tool_streaming("Social-Analyzer", cmd, os.getcwd(), callback, current_logs, consolidated_results, timeout=300)

    # ═══════════════════════════════════════════════════════════════
    # API-based Tools (No CLI needed)
    # ═══════════════════════════════════════════════════════════════

    @classmethod
    async def run_emailrep_live(cls, email: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        """EmailRep.io — email reputation check (free, 100/day)."""
        callback(f"[INFO] Consultando EmailRep.io...")
        try:
            async with httpx.AsyncClient(timeout=15, verify=False) as client:
                resp = await client.get(f"https://emailrep.io/{email}", headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
                if resp.status_code == 200:
                    data = resp.json()
                    reputation = data.get("reputation", "unknown")
                    details = data.get("details", {})
                    breached = details.get("credentials_leaked", False) or details.get("data_breach", False)
                    suspicious = data.get("suspicious", False)
                    disposable = details.get("disposable", False)
                    profiles = details.get("profiles", [])
                    
                    callback(f"[EmailRep] Reputación: {reputation.upper()} | Breach: {'SÍ' if breached else 'NO'} | Disposable: {'SÍ' if disposable else 'NO'}")
                    
                    node = {
                        "type": "email_reputation", "source": "EmailRep",
                        "value": f"Reputation: {reputation}",
                        "data": {"reputation": reputation, "suspicious": suspicious, "breached": breached, "disposable": disposable, "profiles": profiles}
                    }
                    consolidated_results.append(node)
                    
                    for p in profiles:
                        callback(f"[+] EmailRep perfil: {p}")
                        pnode = {"type": "social", "source": "EmailRep", "value": p, "platform": p.capitalize()}
                        if not any(n.get("value") == p for n in consolidated_results):
                            consolidated_results.append(pnode)
                elif resp.status_code == 429:
                    callback("[EmailRep] Rate limit (100/día). Skipping...")
                else:
                    callback(f"[EmailRep] HTTP {resp.status_code}")
        except Exception as e:
            callback(f"[ERROR EmailRep] {str(e)}")

    @classmethod
    async def run_hunter_live(cls, email: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        """Hunter.io — professional email verification (requires API key)."""
        api_key = os.environ.get("HUNTER_API_KEY")
        if not api_key:
            callback("[Hunter] Sin API key. Skipping.")
            return
        callback(f"[INFO] Consultando Hunter.io...")
        try:
            async with httpx.AsyncClient(timeout=15, verify=False) as client:
                resp = await client.get(f"https://api.hunter.io/v2/email-verifier", params={"email": email, "api_key": api_key})
                if resp.status_code == 200:
                    data = resp.json().get("data", {})
                    callback(f"[Hunter] Status: {data.get('status', 'N/A').upper()} | Score: {data.get('score', 0)}/100")
        except Exception as e:
            callback(f"[ERROR Hunter] {str(e)}")

    @classmethod
    async def run_leakcheck_live(cls, email: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        """LeakCheck — verify if email has been leaked."""
        callback(f"[INFO] Consultando LeakCheck...")
        try:
            async with httpx.AsyncClient(timeout=15, verify=False) as client:
                resp = await client.get(f"https://leakcheck.io/api/public", params={"check": email})
                if resp.status_code == 200:
                    data = resp.json()
                    success = data.get("success", False)
                    if success:
                        found = data.get("found", 0)
                        if found > 0:
                            callback(f"[LeakCheck] Encontrado {found} filtraciones para {email}.")
                            node = {
                                "type": "email_leak", "source": "LeakCheck",
                                "value": email,
                                "data": {"leaks": found}
                            }
                            consolidated_results.append(node)
                        else:
                            callback(f"[LeakCheck] Sin filtraciones conocidas.")
                    else:
                        callback(f"[LeakCheck] Error en API: {data.get('error', 'Desconocido')}")
        except Exception as e:
            callback(f"[ERROR LeakCheck] {str(e)}")

    @classmethod
    async def run_listahu(cls, phone: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        """ListaHu — Verificación de números en reportes de estafas en Paraguay."""
        callback(f"[INFO] Consultando historial de fraudes/estafas en ListaHu para {phone}...")
        clean_phone = "".join(filter(str.isdigit, phone))
        try:
            async with httpx.AsyncClient(timeout=10, verify=False) as client:
                res = await client.get(f"https://listahu.org/api/v1/denuncias/?numero={clean_phone}")
                if res.status_code == 200:
                    data = res.json()
                    if data and len(data) > 0:
                        count = len(data)
                        callback(f"[ListaHu] ⚠️ ALERTA: {count} denuncias encontradas asociadas a ese número.")
                        node = {
                            "type": "scam_alert", "source": "ListaHu", 
                            "value": f"{count} Denuncias Activas", 
                            "enriched_zap": True,
                            "meta": {"bio": f"El número {phone} está reportado {count} veces en bases paraguayas de spam/estafa.", "risk_modifier": 45}
                        }
                        if node not in consolidated_results:
                            consolidated_results.append(node)
                    else:
                        callback(f"[ListaHu] Número limpio. Sin denuncias previas.")
        except Exception as e:
            callback(f"[ERROR ListaHu] {str(e)}")
    @classmethod
    async def run_web_search_live(cls, target_name: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        """
        Consults the public web (DuckDuckGo HTML) for news, PDFs, and public mentions of the real name.
        """
        if not target_name or target_name.upper() == "DESCONOCIDO": return
        
        callback(f"[INFO] Buscando huella pública en Web para: {target_name}...")
        try:
            query = f'"{target_name}" ("paraguay" OR "resolucion" OR "pdf" OR "datos")'
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            }
            
            async with httpx.AsyncClient(timeout=10, verify=False) as client:
                res = await client.get(url, headers=headers)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, 'html.parser')
                    results_web = soup.find_all('a', class_='result__snippet')
                    
                    found_count = 0
                    for r in results_web:
                        snippet = r.get_text(strip=True)
                        link = r.get('href', "")
                        if link.startswith("//duckduckgo.com/l/?uddg="):
                            # Decode actual URL
                            link = unquote(link.split("uddg=")[1].split("&")[0])
                            
                        # Relevance check
                        name_parts = target_name.lower().split()
                        if any(p in snippet.lower() for p in name_parts) and not "facebook.com" in link and not "instagram.com" in link:
                            found_count += 1
                            callback(f"[WEB] Hallazgo público: {link[:50]}...")
                            node = {
                                "type": "web_mention",
                                "source": "DuckDuckGo",
                                "value": link,
                                "meta": {"bio": snippet[:150] + "..."}
                            }
                            current_logs.append(f"[WEB] Mencionado en: {link}")
                            if node not in consolidated_results:
                                consolidated_results.append(node)
                        if found_count >= 5: break
                    
                    if found_count == 0:
                        callback("[WEB] No se encontraron menciones web directas relevantes.")
        except Exception as e:
            callback(f"[ERROR WebSearch] {str(e)}")

    @classmethod
    async def run_whatsmyname_live(cls, username: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        """WhatsMyName.app API check — finds profiles across many platforms."""
        callback(f"[INFO] Consultando WhatsMyName (Web API) para: {username}")
        # WhatsMyName usually requires a JSON list of sites. Here we use their public API if available or mock baseline.
        try:
            url = f"https://whatsmyname.app/api/check?username={username}"
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    for site in data.get("found", []):
                        callback(f"[+] WhatsMyName: Encontrado en {site['name']}")
                        node = {"type": "social", "source": "WhatsMyName", "value": site['link'], "platform": site['name']}
                        if not any(n.get("value") == site['link'] for n in consolidated_results):
                            consolidated_results.append(node)
        except Exception as e:
            callback(f"[ERROR WhatsMyName] {str(e)}")

    @classmethod
    def run_truecaller_live(cls, phone: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        """TrueCallerJS — requires local installation and login (zero-login fallback)."""
        callback(f"[INFO] Intentando identificación con TrueCaller...")
        # Note: TrueCallerJS requires a local session. If not present, it fails.
        cmd = ["truecallerjs", "-p", phone, "--json"]
        try:
            # We use a shorter timeout for truecaller
            for line in cls.stream_command(cmd, timeout=15):
                if "{" in line:
                    import json
                    try:
                        data = json.loads(line)
                        name = data.get("name")
                        if name:
                            callback(f"[+] TrueCaller: {name}")
                            node = {"type": "identity", "source": "TrueCaller", "value": name, "meta": {"bio": f"Identificado por TrueCaller: {name}"}}
                            consolidated_results.append(node)
                    except: pass
        except:
            callback("[INFO] TrueCaller: Sesión no disponible o error de CLI.")

    @classmethod
    async def run_phoneinfoga_live(cls, phone: str, callback: Callable, current_logs: List[str], consolidated_results: List[Dict]):
        """Runs PhoneInfoGa scan (zero-login) to identify carrier, location and footprint."""
        callback(f"[INFO] Ejecutando PhoneInfoGa (E.164) para {phone}...")
        cmd = ["phoneinfoga", "scan", "-n", phone]
        
        found_data = {}
        for line in cls.stream_command(cmd, timeout=30):
            clean = line.strip()
            if not clean: continue
            current_logs.append(f"[PhoneInfoGa] {clean}")
            
            # Simple regex to catch useful bits
            if "Carrier:" in clean: found_data["carrier"] = clean.split("Carrier:")[1].strip()
            if "Location:" in clean: found_data["location"] = clean.split("Location:")[1].strip()
            if "Google Search" in clean: callback(f"[PhoneInfoGa] Footprint detectado en Google Search.")

        if found_data:
            node = {
                "type": "phone_intel", "source": "PhoneInfoGa",
                "value": phone,
                "meta": {"bio": f"Carrier: {found_data.get('carrier', 'N/A')} | Loc: {found_data.get('location', 'N/A')}", "location": found_data.get('location')}
            }
            consolidated_results.append(node)
            callback(f"[+] Phone Intel: {found_data.get('carrier', 'N/A')}")
