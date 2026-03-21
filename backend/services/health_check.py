import asyncio
import httpx
import shutil
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class SystemValidator:
    """Validador de Infraestructura OSINTPY v10.0"""
    
    CIVIC_TARGETS = {
        "SET_DNIT": "https://www.set.gov.py/portal/PARAGUAY-SET",
        "CONGRESO_OPEN": "http://datos.congreso.gov.py/opendata/",
        "HACIENDA_NOMINA": "https://servicios.hacienda.gov.py/servicio-nomina/",
        "IPS_CONSULTA": "https://portal.ips.gov.py/"
    }
    
    GLOBAL_TARGETS = {
        "LISTAHU": "https://listahu.org/api/v1/denuncias/",
        "EMAILREP": "https://emailrep.io"
    }
    
    BINARIES = ["social-analyzer", "truecallerjs", "sherlock", "maigret", "node", "python"]

    @classmethod
    async def check_apis(cls) -> Dict[str, str]:
        results = {}
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            tasks = []
            names = []
            
            all_targets = {**cls.CIVIC_TARGETS, **cls.GLOBAL_TARGETS}
            for name, url in all_targets.items():
                tasks.append(client.get(url))
                names.append(name)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for name, resp in zip(names, responses):
                if isinstance(resp, httpx.Response) and resp.status_code < 400:
                    results[name] = "ONLINE ✅"
                else:
                    status = resp.status_code if hasattr(resp, "status_code") else "TIMEOUT"
                    results[name] = f"OFFLINE ❌ ({status})"
        return results

    @classmethod
    def check_binaries(cls) -> Dict[str, str]:
        results = {}
        for binary in cls.BINARIES:
            path = shutil.which(binary)
            results[binary] = "INSTALLED ✅" if path else "MISSING ❌"
        return results

    @classmethod
    async def get_full_health(cls) -> Dict:
        apis = await cls.check_apis()
        binaries = cls.check_binaries()
        return {
            "status": "OPERATIONAL" if all("ONLINE" in v for v in apis.values()) else "DEGRADED",
            "civic_apis": {k: v for k, v in apis.items() if k in cls.CIVIC_TARGETS},
            "global_apis": {k: v for k, v in apis.items() if k in cls.GLOBAL_TARGETS},
            "osint_binaries": binaries
        }
