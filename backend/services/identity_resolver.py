"""
OmniIdentityResolver — Deterministic Identity Resolution Engine
OSINTPY v4.0 Omni-Investigator

100% deterministic. Zero AI dependencies. 
Uses thefuzz for probabilistic name matching and regex for metadata extraction.
"""

import json
import re
import logging
import os
from google import genai
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse

from thefuzz import fuzz


class OmniIdentityResolver:
    """
    Deterministic OSINT Identity Resolution Engine.
    - Fuzzy name matching via thefuzz
    - Zap enrichment indicators
    - Risk score calculation (0-100)
    - Profile merging for recursive searches
    """
    
    PLATFORM_MAP = {
        "github.com": "GitHub", "twitter.com": "X/Twitter", "x.com": "X/Twitter",
        "instagram.com": "Instagram", "facebook.com": "Facebook", "linkedin.com": "LinkedIn",
        "reddit.com": "Reddit", "tiktok.com": "TikTok", "youtube.com": "YouTube",
        "pinterest.com": "Pinterest", "tumblr.com": "Tumblr", "twitch.tv": "Twitch",
        "medium.com": "Medium", "dev.to": "Dev.to", "stackoverflow.com": "StackOverflow",
        "gitlab.com": "GitLab", "soundcloud.com": "SoundCloud", "spotify.com": "Spotify",
        "behance.net": "Behance", "dribbble.com": "Dribbble", "keybase.io": "Keybase",
        "t.me": "Telegram", "telegram.org": "Telegram", "snapchat.com": "Snapchat",
        "vk.com": "VK", "ok.ru": "Odnoklassniki", "flickr.com": "Flickr",
        "threads.net": "Threads",
    }
    
    # ═══════════════════════════════════════════════════════════════
    # CORE: resolve() — The main entry point
    # ═══════════════════════════════════════════════════════════════
    
    @classmethod
    def resolve(cls, raw_logs: List[str], found_nodes: List[Dict],
                query: str, current_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Consolidate raw findings into a structured dossier.
        If current_profile is provided, MERGE new data into it (recursive fusion).
        """
        profile = current_profile if current_profile else cls._empty_profile()
        profile.setdefault("certainty_score", 0)
        
        seen_urls = {fp["url"] for fp in profile.get("digital_footprint", [])}
        
        # 1. Process found_nodes into profile
        for node in found_nodes:
            ntype = node.get("type")
            val = node.get("value")
            source = node.get("source", "Unknown")
            meta = node.get("meta") or node.get("data") or {}
            
            if not val: continue
            
            # Evidence tracking
            evidence_entry = {"type": ntype, "source": source, "value": val}
            if evidence_entry not in profile["evidence"]:
                profile["evidence"].append(evidence_entry)
            
            if ntype == "social":
                normalized = cls._normalize_url(val)
                if normalized and normalized not in seen_urls:
                    seen_urls.add(normalized)
                    platform = node.get("platform") or cls._extract_platform(val)
                    
                    # Zap enrichment detection
                    has_bio = bool(meta.get("bio"))
                    has_location = bool(meta.get("location"))
                    has_name = bool(meta.get("full_name"))
                    enriched_zap = has_bio or has_location or has_name
                    
                    # Confidence metric weighting
                    certainty = 65
                    if enriched_zap: certainty = 85
                    if source in ["PADRON_TSJE", "MINISTERIO_HACIENDA_NOMINA", "SET_DNIT_LOCAL_DB", "TSJE"]: certainty = 100
                    elif "EmailRep" in source or "Holehe" in source or "LeakCheck" in source: certainty = 95
                    
                    fp_entry = {
                        "platform": platform, "url": val, "source": source,
                        "meta": meta, "enriched_zap": enriched_zap, "certainty": certainty
                    }
                    profile["digital_footprint"].append(fp_entry)
                    
                    # Auto-extract photos
                    photo = cls._extract_photo(val)
                    if photo:
                        if photo not in profile["fotos_extraidas"]:
                            profile["fotos_extraidas"].append(photo)
                        if not profile["photo_url"]:
                            profile["photo_url"] = photo
                    
                    # Extract photo from meta if present
                    meta_photo = meta.get("photo") or meta.get("avatar")
                    if meta_photo and meta_photo not in profile["fotos_extraidas"]:
                        profile["fotos_extraidas"].append(meta_photo)
                    
                    # Auto-extract name from enriched metadata
                    if has_name:
                        cls._fuzzy_merge_name(profile, meta["full_name"])
            
            elif ntype == "identity":
                data = node.get("data") or {}
                name = data.get("full_name", "") or val
                if name and len(name) > 3:
                    cls._fuzzy_merge_name(profile, name)
                if data.get("ci"):
                    profile["identity"]["ci"] = data["ci"]
                if data.get("dob"):
                    profile["identity"]["dob"] = data["dob"]
                if data.get("ruc"):
                    profile["fiscal"]["ruc"] = data["ruc"]
                    profile["fiscal"]["status"] = data.get("status", "ACTIVE")
                if data.get("details"):
                    if data["details"] not in profile["fiscal"]["activities"]:
                        profile["fiscal"]["activities"].append(data["details"])
                    
                    # Extract location from Padrón details
                    if "Distrito:" in data["details"]:
                        loc_match = re.search(r"Distrito:\s*([^,]+)(?:,\s*Local:\s*(.+))?", data["details"])
                        if loc_match:
                            loc_str = f"{loc_match.group(1).strip()}"
                            if loc_match.group(2):
                                loc_str += f" ({loc_match.group(2).strip()})"
                            if loc_str not in profile["contacts"]["addresses"]:
                                profile["contacts"]["addresses"].append(loc_str)
            
            elif ntype in ["email_leak", "email"]:
                email_val = val.strip().lower()
                if email_val and email_val not in profile["contacts"]["emails"]:
                    profile["contacts"]["emails"].append(email_val)
            
            elif ntype == "photo":
                if val not in profile["fotos_extraidas"]:
                    profile["fotos_extraidas"].append(val)
                if not profile["photo_url"]:
                    profile["photo_url"] = val
            
            elif ntype in ["phone_info", "phone"]:
                if val and val not in profile["contacts"]["phones"]:
                    profile["contacts"]["phones"].append(val)
            
            elif ntype == "scam_alert":
                profile["threat_intel"].append({
                    "source": source, "value": val, "data": meta
                })
        
        # 2. Heuristic parsing of raw logs
        cls._parse_raw_logs(profile, raw_logs)
        
        # 3. Deterministic Summary (NO AI)
        profile["summary"] = cls._build_summary(profile, query)
        
        # 4. Risk & Certainty Score (v10)
        profile["risk_score"] = cls.calculate_risk_score(profile)
        
        # Certainty Score Logic:
        # Gov Data = 100% baseline
        # Unique IDs (CI/RUC) = High Certainty
        # Social Exposure = Additive
        c_score = 30 # Baseline knowledge
        if profile["identity"].get("ci"): c_score += 40
        if profile["fiscal"].get("ruc"): c_score += 20
        if profile.get("digital_footprint") and len(profile["digital_footprint"]) > 2: c_score += 10
        
        # Boost if govt source is present in evidence
        gov_sources = ["PADRON_TSJE", "SET_DNIT", "CONGRESO", "IPS", "HACIENDA"]
        if any(e.get("source") in gov_sources for e in profile.get("evidence", [])):
            c_score = max(c_score, 90)
            
        profile["certainty_score"] = min(max(int(c_score), 0), 100)
        
        # 5. Build Link Analysis Graph
        profile["graph"] = cls._build_link_analysis_graph(profile, query)
        
        return profile
    
    
    @classmethod
    async def resolve_async(cls, raw_logs: List[str], consolidated_results: List[Dict], query: str = "") -> Dict:
        """Asynchronously resolves the profile and generates a Gemini AI Forensic Report."""
        # 1. First, build the deterministic profile synchronously
        profile = cls.resolve(raw_logs, consolidated_results, query)
        
        # AI Forensics now handled by centralized AIProcessor in task_manager.py
        return profile
        
    @classmethod
    async def _generate_gemini_forensics(cls, profile: Dict) -> str:
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "El Motor LLM (Gemini) está desconectado o falta la API Key."
            
        try:
            client = genai.Client(api_key=api_key)
            prompt = f"""
            Actúa como un Investigador Forense Digital. Redacta un Reporte Forense Analítico (Máximo 3 párrafos, profesional) sobre:
            {json.dumps(profile, indent=2, ensure_ascii=False)}
            """
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"Error en Perfilamiento AI: {str(e)}"
    
    # ═══════════════════════════════════════════════════════════════
    # FUZZY NAME MATCHING
    # ═══════════════════════════════════════════════════════════════
    
    @classmethod
    def _fuzzy_merge_name(cls, profile: Dict, new_name: str):
        """Use thefuzz to decide whether to merge or list as alternative."""
        if not new_name:
            return
        new_name = str(new_name).strip()
        if not new_name or new_name.upper() == "DESCONOCIDO":
            return
        
        current = profile["identity"].get("full_name")
        
        if not current or current == "DESCONOCIDO":
            profile["identity"]["full_name"] = new_name
            return
        
        # Compare with thefuzz
        ratio = fuzz.ratio(current.lower(), new_name.lower())
        partial = fuzz.partial_ratio(current.lower(), new_name.lower())
        
        if ratio >= 85 or partial >= 90:
            # High confidence match — keep the longer/more complete name
            if len(new_name) > len(current):
                profile["identity"]["full_name"] = new_name
        elif ratio >= 70:
            # Medium confidence — list as possible alternative
            if new_name not in profile.get("possible_alternatives", []):
                profile.setdefault("possible_alternatives", []).append(new_name)
        else:
            # Low confidence — different person entirely
            if new_name not in profile.get("possible_alternatives", []):
                profile.setdefault("possible_alternatives", []).append(new_name)
    
    # ═══════════════════════════════════════════════════════════════
    # RAW LOG PARSING
    # ═══════════════════════════════════════════════════════════════
    
    @classmethod
    def _parse_raw_logs(cls, profile: Dict, raw_logs: List[str]):
        """Extract structured data from raw tool output logs using regex."""
        for line in raw_logs:
            # 1. RUC extraction
            ruc_match = re.search(r"RUC:\s*(\d+-\d+)", line)
            if ruc_match:
                profile["fiscal"]["ruc"] = ruc_match.group(1)
                profile["fiscal"]["status"] = "ACTIVE"
            
            # Blocked/suspended RUC
            if re.search(r"(bloqueado|suspendido|cancelado|inhabilitado)", line, re.I):
                profile["fiscal"]["status"] = "BLOCKED"
            
            # 2. Email extraction
            email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w{2,}", line)
            if email_match:
                email = email_match.group(0).lower()
                if email not in profile["contacts"]["emails"] and not email.endswith((".png", ".jpg", ".gif", ".webp")):
                    profile["contacts"]["emails"].append(email)
            
            # 3. Phone extraction (International & Paraguay)
            phone_pattern = r'(\+?595|0?9)[2-9]\d{7,8}' # Simplified PY focus
            ph_match = re.search(phone_pattern, line)
            if ph_match:
                ph = ph_match.group(0).strip()
                if ph not in profile["contacts"]["phones"] and len(ph) >= 9:
                    profile["contacts"]["phones"].append(ph)

            # Broad International Phone Regex
            intl_phone = re.search(r'\+?\d{1,3}[\s-]?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}', line)
            if intl_phone:
                ph = intl_phone.group(0).strip()
                if ph not in profile["contacts"]["phones"] and len(ph) >= 9:
                    profile["contacts"]["phones"].append(ph)
            
            # 4. Photo URL extraction from logs (Zap ⚡)
            photo_match = re.search(r'(https?://\S+\.(?:jpg|jpeg|png|webp|gif))', line, re.I)
            if photo_match:
                photo_url = photo_match.group(1)
                if photo_url not in profile["fotos_extraidas"]:
                    profile["fotos_extraidas"].append(photo_url)
            
            # 5. Bio/Location extraction (Zap enrichment)
            bio_match = re.search(r'\[?\+?\]?\s*(?:Bio|About|Summary):\s*(.+)', line, re.I)
            if bio_match:
                bio = bio_match.group(1).strip()
                if bio and len(bio) > 5:
                    if bio not in profile.get("extracted_bios", []):
                        profile.setdefault("extracted_bios", []).append(bio)
            
            location_match = re.search(r'\[?\+?\]?\s*(?:Location|Place|Address):\s*(.+)', line, re.I)
            if location_match:
                loc = location_match.group(1).strip()
                if loc and loc not in profile["contacts"].get("addresses", []):
                    profile["contacts"].setdefault("addresses", []).append(loc)
    
    # ═══════════════════════════════════════════════════════════════
    # RISK SCORE ENGINE
    # ═══════════════════════════════════════════════════════════════
    
    @classmethod
    def calculate_risk_score(cls, profile: Dict) -> int:
        """
        Omni-Investigator Risk Scoring (v10):
        0-30: Bajo | 31-60: Moderado | 61-80: Alto | 81-100: Crítico
        """
        risk = 0
        
        # 1. Digital Footprint (+5 per node)
        risk += len(profile.get("digital_footprint", [])) * 5
        
        # 2. Email Breaches (+20 per breach)
        rep = profile.get("email_reputation") or {}
        if rep.get("breached"):
            risk += 20
        if rep.get("malicious"):
            risk += 40
        
        # 3. Fiscal Status (+30 if blocked)
        if profile["fiscal"].get("status") == "BLOCKED":
            risk += 30
            
        # 4. Threat Intel (ListaHu +40)
        for ti in profile.get("threat_intel", []):
            source = ti.get("source", "").upper()
            if "LISTAHU" in source:
                risk += 40
            elif "SCAM" in source or "FRAUD" in source:
                risk += 25
        
        # 5. Exposed Contacts
        risk += len(profile["contacts"].get("emails", [])) * 5
        risk += len(profile["contacts"].get("phones", [])) * 10
        
        return min(risk, 100)
    
    # ═══════════════════════════════════════════════════════════════
    # MERGE PROFILES (for recursive searches)
    # ═══════════════════════════════════════════════════════════════
    
    @classmethod
    def merge_profiles(cls, existing: Dict, new_data: Dict) -> Dict:
        """Merge new_data into existing profile deterministically."""
        merged = dict(existing)
        
        # Identity: fuzzy merge name
        new_name = new_data.get("identity", {}).get("full_name")
        if new_name:
            cls._fuzzy_merge_name(merged, new_name)
        
        if new_data.get("identity", {}).get("ci"):
            merged["identity"]["ci"] = new_data["identity"]["ci"]
        if new_data.get("identity", {}).get("dob"):
            merged["identity"]["dob"] = new_data["identity"]["dob"]
        
        # Fiscal
        if new_data.get("fiscal", {}).get("ruc"):
            merged["fiscal"]["ruc"] = new_data["fiscal"]["ruc"]
            merged["fiscal"]["status"] = new_data["fiscal"].get("status", "ACTIVE")
        
        # Array dedup via sets
        for key in ["emails", "phones", "addresses"]:
            existing_vals = set(merged.get("contacts", {}).get(key, []))
            new_vals = set(new_data.get("contacts", {}).get(key, []))
            merged.setdefault("contacts", {})[key] = list(existing_vals | new_vals)
        
        merged["organizations"] = list(set(merged.get("organizations", []) + new_data.get("organizations", [])))
        
        # Digital footprint by URL
        seen_urls = {fp["url"] for fp in merged.get("digital_footprint", [])}
        for fp in new_data.get("digital_footprint", []):
            if fp["url"] not in seen_urls:
                merged.setdefault("digital_footprint", []).append(fp)
                seen_urls.add(fp["url"])
        
        # Evidence dedup
        seen_ev = {json.dumps(e, sort_keys=True) for e in merged.get("evidence", [])}
        for e in new_data.get("evidence", []):
            e_str = json.dumps(e, sort_keys=True)
            if e_str not in seen_ev:
                merged.setdefault("evidence", []).append(e)
        
        # Fotos
        merged["fotos_extraidas"] = list(set(
            merged.get("fotos_extraidas", []) + new_data.get("fotos_extraidas", [])
        ))
        
        # Web Mentions
        seen_web = {w.get("url") for w in merged.get("web_mentions", [])}
        for w in new_data.get("web_mentions", []):
            if w.get("url") not in seen_web:
                merged.setdefault("web_mentions", []).append(w)
                seen_web.add(w.get("url"))
        
        if not merged.get("photo_url") and new_data.get("photo_url"):
            merged["photo_url"] = new_data["photo_url"]
        if not merged.get("email_reputation") and new_data.get("email_reputation"):
            merged["email_reputation"] = new_data["email_reputation"]
        
        # Threat intel
        merged["threat_intel"] = merged.get("threat_intel", []) + new_data.get("threat_intel", [])
        
        # Notes
        if new_data.get("notes"):
            existing_notes = merged.get("notes", "")
            merged["notes"] = (existing_notes + "\n" + new_data["notes"]).strip() if existing_notes else new_data["notes"]
        
        # Recalculate
        merged["risk_score"] = cls.calculate_risk_score(merged)
        merged["summary"] = cls._build_summary(merged, merged.get("identity", {}).get("full_name", ""))
        merged["graph"] = cls._build_link_analysis_graph(merged, merged.get("identity", {}).get("full_name", ""))
        
        return merged
    
    # ═══════════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════════
    
    @staticmethod
    def _empty_profile() -> Dict:
        return {
            "identity": {"full_name": None, "ci": None, "dob": None},
            "fiscal": {"ruc": None, "status": None, "activities": []},
            "contacts": {"emails": [], "phones": [], "addresses": []},
            "digital_footprint": [],
            "fotos_extraidas": [],
            "risk_score": 0,
            "summary": "",
            "photo_url": None,
            "email_reputation": None,
            "organizations": [],
            "related_emails": [],
            "evidence": [],
            "threat_intel": [],
            "possible_alternatives": [],
            "notes": "",
            "web_mentions": [],
            "graph": {"nodes": [], "edges": []}
        }
    
    @classmethod
    def _extract_platform(cls, url: str) -> str:
        try:
            domain = urlparse(url).netloc.lower().replace("www.", "")
            for key, name in cls.PLATFORM_MAP.items():
                if key in domain:
                    return name
            return domain.split(".")[0].capitalize()
        except:
            return "Unknown"
    
    @staticmethod
    def _normalize_url(url: str) -> str:
        url = url.rstrip("/").lower()
        url = re.sub(r'^https?://(www\.)?', '', url)
        return url
    
    @staticmethod
    def _extract_photo(url: str) -> str:
        if "github.com" in url and "%" not in url:
            username = url.rstrip("/").split("/")[-1]
            if username and len(username) > 1:
                return f"https://github.com/{username}.png"
        if "twitter.com" in url or "x.com" in url:
            username = url.rstrip("/").split("/")[-1]
            if username and "%" not in username:
                return f"https://unavatar.io/twitter/{username}"
        return ""
    
    @staticmethod
    def _build_summary(profile: Dict, query: str = "") -> str:
        """Build intelligence summary deterministically."""
        parts = []
        name = profile.get("identity", {}).get("full_name")
        
        if name and name != "DESCONOCIDO":
            parts.append(f"Sujeto identificado como {name}.")
        else:
            parts.append(f"Sujeto bajo investigación: {query}.")
        
        fp_count = len(profile.get("digital_footprint", []))
        if fp_count > 0:
            parts.append(f"{fp_count} perfiles digitales detectados.")
        
        emails = profile.get("contacts", {}).get("emails", [])
        if emails:
            parts.append(f"{len(emails)} correos electrónicos encontrados.")
        
        phones = profile.get("contacts", {}).get("phones", [])
        if phones:
            parts.append(f"{len(phones)} teléfonos detectados.")
        
        ruc = profile.get("fiscal", {}).get("ruc")
        if ruc:
            status = profile.get("fiscal", {}).get("status", "ACTIVE")
            parts.append(f"Registro fiscal (RUC): {ruc} — Estado: {status}.")
        
        risk = profile.get("risk_score", 0)
        if risk > 80:
            parts.append("⚠️ RIESGO CRÍTICO: Exposición digital extrema detectada.")
        elif risk > 60:
            parts.append("Exposición digital elevada. Se recomienda monitoreo continuo.")
        elif risk > 30:
            parts.append("Exposición digital moderada.")
        
        alts = profile.get("possible_alternatives", [])
        if alts:
            parts.append(f"Identidades alternativas posibles: {', '.join(alts[:3])}.")
        
        # Extracted Photos count
        fotos = profile.get("fotos_extraidas", [])
        if fotos:
            parts.append(f"{len(fotos)} fotografía(s) extraída(s).")
            
        menciones = len(profile.get("web_mentions", []))
        if menciones > 0:
            parts.append(f"{menciones} mención(es) en fuentes web públicas.")
        
        return " ".join(parts) if parts else "Análisis determinista completado."

    @classmethod
    def _build_link_analysis_graph(cls, profile: Dict, query: str) -> Dict[str, List[Dict]]:
        """
        Generates nodes and edges for a Maltego-style link analysis graph.
        """
        nodes = []
        edges = []
        
        target_name = profile.get("identity", {}).get("full_name") or query or "Target"
        target_id = f"node_target_{target_name.replace(' ', '_')}"
        
        nodes.append({
            "id": target_id,
            "label": target_name,
            "type": "Target",
            "group": "identity"
        })
        
        # Digital Footprint Nodes
        for fp in profile.get("digital_footprint", []):
            url = fp.get("url", "")
            if not url: continue
            node_id = f"node_social_{url}"
            nodes.append({
                "id": node_id,
                "label": fp.get("platform", "Social Media"),
                "sublabel": url.split("/")[-1] if "/" in url else url,
                "type": "SocialProfile",
                "group": "social"
            })
            edges.append({"source": target_id, "target": node_id, "label": "HAS_PROFILE"})
            
        # Web Mentions Nodes
        for wm in profile.get("web_mentions", []):
            url = wm.get("url", "")
            if not url: continue
            node_id = f"node_web_{url}"
            domain = urlparse(url).netloc.replace("www.", "")
            nodes.append({
                "id": node_id,
                "label": domain,
                "sublabel": "Web Mention",
                "type": "WebMention",
                "group": "web"
            })
            edges.append({"source": target_id, "target": node_id, "label": "MENTIONED_IN"})
            
        # Emails
        for email in profile.get("contacts", {}).get("emails", []):
            node_id = f"node_email_{email}"
            nodes.append({
                "id": node_id,
                "label": email,
                "type": "EmailAddress",
                "group": "contact"
            })
            edges.append({"source": target_id, "target": node_id, "label": "OWNS_EMAIL"})
            
        # Phones
        for phone in profile.get("contacts", {}).get("phones", []):
            node_id = f"node_phone_{phone}"
            nodes.append({
                "id": node_id,
                "label": phone,
                "type": "PhoneNumber",
                "group": "contact"
            })
            edges.append({"source": target_id, "target": node_id, "label": "OWNS_PHONE"})
            
        # Addresses/Locations
        for addr in profile.get("contacts", {}).get("addresses", []):
            node_id = f"node_loc_{addr}"
            nodes.append({
                "id": node_id,
                "label": addr,
                "type": "Location",
                "group": "location"
            })
            edges.append({"source": target_id, "target": node_id, "label": "ASSOCIATED_LOCATION"})
            
        # Fiscal
        ruc = profile.get("fiscal", {}).get("ruc")
        if ruc:
            node_id = f"node_ruc_{ruc}"
            nodes.append({
                "id": node_id,
                "label": f"RUC: {ruc}",
                "type": "Company/TaxID",
                "group": "fiscal"
            })
            edges.append({"source": target_id, "target": node_id, "label": "REGISTERED_TAX_ID"})
            
        # Threat Intel
        for threat in profile.get("threat_intel", []):
            val = threat.get("value", "Threat")
            node_id = f"node_threat_{val}"
            nodes.append({
                "id": node_id,
                "label": threat.get("source", "ThreatIntel"),
                "sublabel": val,
                "type": "Threat",
                "group": "threat"
            })
            edges.append({"source": target_id, "target": node_id, "label": "FLAGGED_IN"})

        return {"nodes": nodes, "edges": edges}


# Backwards compatibility alias
IdentityResolver = OmniIdentityResolver
