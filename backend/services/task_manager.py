import asyncio
import uuid
import time
from typing import Dict, Any, List, Callable
import logging

logger = logging.getLogger("kuarahy_task_manager")

class LocalTaskRunner:
    """
    In-Process Task Runner (Windows-Friendly)
    Full OSINT Deep Dive with smart query routing.
    """
    _instance = None
    tasks: Dict[str, Dict] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LocalTaskRunner, cls).__new__(cls)
        return cls._instance

    def create_task(self, target_data: dict) -> str:
        task_id = str(uuid.uuid4())
        
        disp = target_data.get("alias") or target_data.get("nombre") or target_data.get("email") or target_data.get("ci_ruc") or "OmniTarget"
        
        self.tasks[task_id] = {
            "id": task_id,
            "status": "pending",
            "progress": 5,
            "logs": ["Tarea encolada para OMNI-INVESTIGATOR..."],
            "found_nodes": [],
            "profile": None,
            "target_data": target_data,
            "query": disp,
            "query_type": "omni",
            "created_at": time.time(),
            "active_tools": []
        }
        return task_id

    def update_task_state(self, task_id: str, state: str = None, meta: Dict = None):
        if task_id in self.tasks:
            if state: self.tasks[task_id]["status"] = state
            if meta:
                for key in ('logs', 'progress', 'found_nodes', 'profile', 'active_tools'):
                    if key in meta:
                        self.tasks[task_id][key] = meta[key]

    def get_task_status(self, task_id: str) -> Dict:
        return self.tasks.get(task_id, {"status": "not_found"})

    async def run_engine(self, task_id: str):
        from agents.osint_tools import OSINTToolAgent
        from agents.py_gov import ParaguayDataAgent
        from agents.persistence import ProfilePersistenceAgent
        from services.identity_resolver import OmniIdentityResolver

        task = self.tasks[task_id]
        query = task["query"]
        query_type = task["query_type"]
        current_logs = task["logs"]
        target_data = task.get("target_data", {})
        
        ci_ruc = target_data.get("ci_ruc", "").strip()
        nombre = target_data.get("nombre", "").strip()
        alias = target_data.get("alias", "").strip()
        email = target_data.get("email", "").strip()
        telefono = target_data.get("telefono", "").strip()

        consolidated_results: List[Dict] = []
        tool_count = 0
        total_tools = self._estimate_tool_count(query_type)
        
        # Redis Logging Setup
        import redis
        rd = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        def log_callback(line: str):
            if not line: return
            current_logs.append(line)
            # Push to Redis for real-time frontend streaming
            try:
                rd.publish(f"task_logs_{task_id}", line)
            except: pass
            
            progress = min(int((tool_count / max(total_tools, 1)) * 90 + 5), 98)
            self.update_task_state(task_id, state="executing", meta={
                'logs': current_logs[-50:],
                'progress': progress,
                'found_nodes': list(consolidated_results)
            })

        def tool_done():
            nonlocal tool_count
            tool_count += 1

        try:
            self.update_task_state(task_id, state="executing")
            log_callback(f"[INIT] Motor OMNI-INVESTIGATOR iniciando para: {query}")
            notas = target_data.get("notas_adicionales", "").strip()

            # User-provided seeds and rejected nodes (for interactive refinement)
            extra_seeds = task.get("new_seeds", [])
            verified_nodes = task.get("verified_nodes", []) # New: nodes explicitly verified by user
            rejected_nodes = task.get("rejected_nodes", [])
            rejected_values = {r.get("value") for r in rejected_nodes if r.get("value")}
            
            def is_rejected(val: str) -> bool:
                return val in rejected_values
            
            # THE RECURSIVE ENGINE: Promote verified findings to targets
            recursive_targets = []
            for vn in verified_nodes:
                val = vn.get("value")
                if not val or is_rejected(val): continue
                vtype = vn.get("type")
                if vtype in ("social", "username", "email", "phone"):
                    recursive_targets.append({"value": val, "type": vtype})
            
            # The REAL name(s) found from government data
            real_names: List[str] = []

            # Combine original query with new seeds and recursive targets
            osint_username_targets = []
            osint_email_targets = []
            osint_phone_targets = []

            # 1. Handle primary Omni targets
            if alias: osint_username_targets.append(alias)
            if email: 
                osint_email_targets.append(email)
                osint_username_targets.append(email.split("@")[0]) # Infer alias from email
            if telefono: osint_phone_targets.append(telefono)

            # 2. Handle extra seeds (manual injection)
            for seed in extra_seeds:
                if "@" in seed: osint_email_targets.append(seed)
                elif seed.startswith("+") or (seed.isdigit() and len(seed) > 8): osint_phone_targets.append(seed)
                else: osint_username_targets.append(seed)
            
            # 3. Handle recursive targets (verified findings)
            for rt in recursive_targets:
                if rt["type"] == "email": osint_email_targets.append(rt["value"])
                elif rt["type"] == "phone": osint_phone_targets.append(rt["value"])
                elif rt["type"] in ("social", "username"):
                    # Extract username from URL if social
                    val = rt["value"]
                    if val.startswith("http"):
                        username = val.rstrip("/").split("/")[-1]
                        if username and len(username) > 2: osint_username_targets.append(username)
                    else:
                        osint_username_targets.append(val)

            # Deduplicate targets
            osint_username_targets = list(set(osint_username_targets))
            osint_email_targets = list(set(osint_email_targets))
            osint_phone_targets = list(set(osint_phone_targets))

            # ═══════════════════════════════════════════════════════
            # FASE 1: Civic & National Data (Gov/HUMINT)
            # ═══════════════════════════════════════════════════════
            if ci_ruc or nombre:
                query_gov = ci_ruc if ci_ruc else nombre
                q_type = "ci" if ci_ruc else "username"
                log_callback(f"[GOV] Consultando Registros Nacionales para {query_gov}...")
                gov_hits = await ParaguayDataAgent.search_all(query_gov, q_type, log_callback)
                for hit in gov_hits:
                    name = hit.get("full_name", "")
                    if is_rejected(name): continue
                    node = {"type": "identity", "source": hit["source"], "value": name, "data": hit}
                    consolidated_results.append(node)
                    if name and name not in real_names: real_names.append(name)
                
                # Pivot: If we found real names from Gov, append to Social OSINT
                for name in real_names:
                    if name not in osint_username_targets:
                        osint_username_targets.append(name)
            
            # Deduplicate targets
            osint_username_targets = list(set(osint_username_targets))
            osint_email_targets = list(set(osint_email_targets))
            osint_phone_targets = list(set(osint_phone_targets))
            
            # Update estimate for UI
            total_tools = (len(osint_username_targets) * 3) + (len(osint_email_targets) * 2) + len(osint_phone_targets) + 1
            self.update_task_state(task_id, meta={'total_tools': total_tools, 'completed_tools': 0})
            
            def tool_done():
                nonlocal tool_count
                tool_count += 1
                progress = min(int((tool_count / max(total_tools, 1)) * 90 + 5), 98)
                self.update_task_state(task_id, meta={'completed_tools': tool_count, 'progress': progress})

            # ═══════════════════════════════════════════════════════
            # PHASE 2: Username OSINT (Concurrent Execution - Tier 2)
            # ═══════════════════════════════════════════════════════
            async def run_threaded_tool(func, tool_name, tgt):
                # Check health status from Phase 0
                health = getattr(self, '_health_status', {}).get('osint_binaries', {})
                if tool_name.lower() in health and "MISSING" in health[tool_name.lower()]:
                    log_callback(f"[SKIP] {tool_name} no está instalado.")
                    return
                
                self.update_task_state(task_id, meta={'active_tools': [tool_name]})
                try:
                    # Aggressive 45s timeout per tool to prevent backend stalls
                    await asyncio.wait_for(
                        asyncio.to_thread(func, tgt, log_callback, current_logs, consolidated_results),
                        timeout=45.0
                    )
                except asyncio.TimeoutError:
                    log_callback(f"[TIMEOUT] {tool_name} excedió el límite de tiempo. Continuando con datos parciales.")
                except Exception as e:
                    log_callback(f"[ERROR] {tool_name} falló: {str(e)}")
                tool_done()

            async def run_async_tool(func, tool_name, tgt):
                health = getattr(self, '_health_status', {}).get('civic_apis', {})
                if tool_name in health and "OFFLINE" in health[tool_name]:
                    log_callback(f"[SKIP] {tool_name} está fuera de línea.")
                    return

                self.update_task_state(task_id, meta={'active_tools': [tool_name]})
                try:
                    await asyncio.wait_for(
                        func(tgt, log_callback, current_logs, consolidated_results),
                        timeout=30.0
                    )
                except asyncio.TimeoutError:
                    log_callback(f"[TIMEOUT] API {tool_name} no respondió a tiempo.")
                except Exception as e:
                    log_callback(f"[ERROR] API {tool_name} falló: {str(e)}")
                tool_done()

            # Execute Core Username OSINT in Massive Parallel
            username_tasks = []
            for target in osint_username_targets:
                if is_rejected(target): continue
                log_callback(f"[OSINT] Escaneando huella digital agresivamente: {target}")
                
                username_tasks.extend([
                    run_threaded_tool(OSINTToolAgent.run_sherlock_live, 'Sherlock', target),
                    run_threaded_tool(OSINTToolAgent.run_maigret_live, 'Maigret', target),
                    run_threaded_tool(OSINTToolAgent.run_social_analyzer_live, 'Social-Analyzer', target),
                    run_threaded_tool(OSINTToolAgent.run_blackbird_live, 'Blackbird', target),
                    run_async_tool(OSINTToolAgent.run_whatsmyname_live, 'WhatsMyName', target)
                ])
            
            if username_tasks:
                self.update_task_state(task_id, meta={'active_tools': ['Multi-Scan']})
                await asyncio.gather(*username_tasks)

            # ═══════════════════════════════════════════════════════
            # PHASE 3: Auto-Recursion (Lead Discovery)
            # ═══════════════════════════════════════════════════════
            secondary_leads = []
            for node in consolidated_results:
                if "meta" in node and "full_name" in node["meta"]:
                    name = node["meta"]["full_name"]
                    if name not in real_names and not is_rejected(name) and len(name.split()) >= 2:
                        secondary_leads.append(name)
                        real_names.append(name)
            
            if secondary_leads:
                log_callback(f"[AUTO-RECURSE] Encontrados {len(secondary_leads)} posibles nombres reales. Profundizando...")
                for lead in secondary_leads:
                    log_callback(f"[OSINT] Escaneando lead automático: {lead}")
                    # Run a targeted Maigret search for the lead as a name
                    self.update_task_state(task_id, meta={'active_tools': ['Auto-Maigret']})
                    await asyncio.to_thread(OSINTToolAgent.run_maigret_live, lead, log_callback, current_logs, consolidated_results)
                    # We don't increment tool_done here to not mess with the progress bar too much, or we could update total_tools
            
            # ═══════════════════════════════════════════════════════
            # PHASE 4: Email OSINT (Concurrent Holehe, EmailRep, Hunter)
            # ═══════════════════════════════════════════════════════
            # ═══════════════════════════════════════════════════════
            # PHASE 4: Email OSINT (Concurrent Holehe, EmailRep, Hunter, LeakCheck)
            # ═══════════════════════════════════════════════════════
            email_tasks = []
            for email_target in osint_email_targets:
                if is_rejected(email_target): continue
                log_callback(f"[OSINT] Verificando email agresivamente: {email_target}")
                
                email_tasks.extend([
                    run_threaded_tool(OSINTToolAgent.run_holehe_live, 'Holehe', email_target),
                    run_async_tool(OSINTToolAgent.run_emailrep_live, 'EmailRep', email_target),
                    run_async_tool(OSINTToolAgent.run_hunter_live, 'Hunter', email_target),
                    run_async_tool(OSINTToolAgent.run_leakcheck_live, 'LeakCheck', email_target)
                ])
            
            if email_tasks:
                self.update_task_state(task_id, meta={'active_tools': ['Email-Intel']})
                await asyncio.gather(*email_tasks)

            # ═══════════════════════════════════════════════════════
            # FASE 4.5: DEEPENING PASS — Holehe alias → Maigret
            # ═══════════════════════════════════════════════════════
            deepening_aliases = []
            for node in consolidated_results:
                if node.get("type") == "email_leak":
                    leak_val = node.get("value", "")
                    # Try to extract username from holehe hit (usually format "[+] service : email@")
                    alias_from_email = None
                    for email_t in osint_email_targets:
                        if "@" in email_t:
                            alias_from_email = email_t.split("@")[0]
                            break
                    if alias_from_email and alias_from_email not in osint_username_targets:
                        deepening_aliases.append(alias_from_email)
            
            if deepening_aliases:
                log_callback(f"[DEEPENING] Holehe descubrió leads. Profundizando con Maigret...")
                for da in list(set(deepening_aliases))[:3]:
                    log_callback(f"[OSINT] Deepening Pass: {da}")
                    self.update_task_state(task_id, meta={'active_tools': ['Maigret-Deep']})
                    await asyncio.to_thread(OSINTToolAgent.run_maigret_live, da, log_callback, current_logs, consolidated_results)

            # ═══════════════════════════════════════════════════════
            # FASE 4.8: WEB INTEL (DuckDuckGo Public Footprint)
            # ═══════════════════════════════════════════════════════
            if real_names:
                for target_name in list(set(real_names))[:2]: # Max 2 names to avoid spamming DDG
                    self.update_task_state(task_id, meta={'active_tools': ['WebIntel']})
                    await OSINTToolAgent.run_web_search_live(target_name, log_callback, current_logs, consolidated_results)
                    # We don't advance tool_count to not break progress estimation, or we could add to total_tools earlier.

            # ═══════════════════════════════════════════════════════
            # FASE 5: Threat Intel (ListaHu & Phone OSINT)
            # ═══════════════════════════════════════════════════════
            if osint_phone_targets:
                self.update_task_state(task_id, meta={'active_tools': ['ThreatIntel', 'PhoneInfoGa', 'TrueCaller']})
                for phone in osint_phone_targets:
                    # Native Lib Check
                    OSINTToolAgent.run_phone_osint(phone, log_callback, consolidated_results)
                    # ListaHu Real Async Check
                    await OSINTToolAgent.run_listahu(phone, log_callback, current_logs, consolidated_results)
                    # PhoneInfoGa Scan
                    await OSINTToolAgent.run_phoneinfoga_live(phone, log_callback, current_logs, consolidated_results)
                    # TrueCaller
                    await asyncio.to_thread(OSINTToolAgent.run_truecaller_live, phone, log_callback, current_logs, consolidated_results)
                tool_done()

            # Filter rejected nodes
            consolidated_results = [n for n in consolidated_results if not is_rejected(n.get("value", ""))]

            # ═══════════════════════════════════════════════════════
            # PHASE 6: FINAL CONSOLIDATION & AI PROFILER
            # ═══════════════════════════════════════════════════════
            self.update_task_state(task_id, meta={'progress': 99, 'active_tools': ['Gemini Executive AI']})
            log_callback("[RESOLVER] Generando Análisis Forense (Gemini LLM) y consolidando dossier...")
            profile = await OmniIdentityResolver.resolve_async(current_logs, consolidated_results, query)
            
            # News Intel Pass
            news_hits = []
            if real_names:
                from news import NewsScraper
                for name in real_names[:1]:
                    status_update(f"[NEWS] Buscando menciones en prensa paraguaya: {name}")
                    news_hits = await NewsScraper.get_combined_news(name)
                    for n in news_hits:
                        discovered_results.append({
                            "type": "news_record", "source": n['source'], "value": n['title'], "meta": n
                        })

            # FASE 4: AI Summary Integration (New SDK)
            from ai.processor import AIProcessor
            try:
                ai_proc = AIProcessor()
                profile["semantic_summary"] = await ai_proc.generate_semantic_summary(profile, news_hits)
            except Exception as ai_err:
                logger.error(f"AI SDK Error: {ai_err}")
                profile["semantic_summary"] = profile.get("summary", "Análisis AI fallido.")
            
            profile["task_id"] = task_id
            # Store notas_adicionales from intake form
            if notas:
                profile["notes"] = notas
            
            tool_done()
            
            # ═══════════════════════════════════════════════════════
            # PHASE 7: Persistent Storage (Smart Merge)
            # ═══════════════════════════════════════════════════════
            ProfilePersistenceAgent.merge_and_save(task_id, query_type, query, profile)
            
            # PHASE 8: Ocas-Scout Journaling
            metrics = {
                "total_tools_ran": tool_count,
                "nodes_found": len(consolidated_results),
                "risk_score": profile.get("risk_score", 0),
                "duration_seconds": time.time() - task.get("created_at", time.time())
            }
            ProfilePersistenceAgent.ocas_scout_journal(task_id, metrics)
            
            self.update_task_state(task_id, state="completed", meta={
                'progress': 100,
                'logs': current_logs,
                'profile': profile,
                'processed_profile_id': profile.get("id") or task_id,
                'active_tools': []
            })
            
        except Exception as e:
            logger.error(f"Deep Dive failed: {e}", exc_info=True)
            self.update_task_state(task_id, state="failed", meta={
                'logs': current_logs + [f"[SYSTEM ERROR] {str(e)}"],
                'active_tools': []
            })

    def _estimate_tool_count(self, query_type: str) -> int:
        # This function is now an initial estimate, the actual total_tools is calculated dynamically
        if query_type in ("username",):
            return 4  # Sherlock + Maigret + Blackbird + AI
        elif query_type in ("ci", "ruc"):
            return 6  # GOV + Sherlock + Maigret + Blackbird + AI
        elif query_type == "email":
            return 6  # Sherlock + Maigret + Blackbird + Holehe + EmailRep + AI
        elif query_type == "phone":
            return 2  # Phone + AI
        return 4

task_manager = LocalTaskRunner()
