from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from agents.py_gov import ParaguayGovAgent
from agents.osint_tools import OSINTToolAgent

router = APIRouter(prefix="/api/search", tags=["search"])

class SearchQuery(BaseModel):
    query: str
    type: str  # ci, ruc, name, phone, email

@router.post("/")
async def perform_search(search_query: SearchQuery):
    results = []
    
    # 1. Direct Paraguayan Gov Search
    if search_query.type in ["ci", "ruc", "name"]:
        gov_results = []
        if search_query.type == "ci":
            gov_results.append(ParaguayGovAgent.query_padron(search_query.query))
            gov_results.append(ParaguayGovAgent.query_ips(search_query.query))
        elif search_query.type == "ruc":
            gov_results.append(ParaguayGovAgent.query_ruc(search_query.query))
        
        for res in gov_results:
            results.append({
                "source": res["source"],
                "title": f"Registro Oficial: {search_query.query}",
                "description": str(res["data"]),
                "type": "gov"
            })

    # 2. Global OSINT Search (Sherlock/Maigret)
    if search_query.type in ["name", "email"]:
        osint_results = OSINTToolAgent.run_username_search(search_query.query)
        results.append({
            "source": "OSINT Tools",
            "title": f"Huella Digital: {search_query.query}",
            "description": f"Encontrado en {len(osint_results)} plataformas.",
            "type": "osint",
            "data": osint_results
        })

    return {
        "query": search_query.query,
        "type": search_query.type,
        "results": results
    }
