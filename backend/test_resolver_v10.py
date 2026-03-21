import asyncio
from services.identity_resolver import OmniIdentityResolver

async def test_v10_resolver():
    print("--- OSINTPY v10: Identity Resolver Unit Test ---")
    
    logs = [
        "[Maigret] Bio: Investigador OSINT y DevOps. Paraguay.", 
        "[Social-Analyzer] Location: Asuncion", 
        "[CLI] Found Phone: +595981123456",
        "RUC: 1234567-8",
        "[DEBUG] Profile Photo found: https://github.com/alexzena.png"
    ]
    
    nodes = [
        {
            "type": "identity", 
            "value": "Alexandra Zena", 
            "source": "TSJE", 
            "data": {"ci": "8765432", "full_name": "Alexandra Zena"}
        },
        {
            "type": "scam_alert", 
            "value": "Reporte 123", 
            "source": "ListaHu",
            "meta": {"risk_modifier": 40}
        }
    ]
    
    # Run sync resolve
    profile = OmniIdentityResolver.resolve(logs, nodes, "Alexandra")
    
    print(f"Name Resolved: {profile['identity'].get('full_name')}")
    print(f"CI: {profile['identity'].get('ci')}")
    print(f"RUC: {profile['fiscal'].get('ruc')}")
    print(f"Risk Score: {profile['risk_score']}")
    print(f"Certainty Score: {profile['certainty_score']}")
    print(f"Extracted Bios: {profile.get('extracted_bios')}")
    print(f"Identified Phones: {profile['contacts'].get('phones')}")
    print(f"Found Photos: {profile.get('fotos_extraidas')}")
    
    assert profile['identity']['full_name'] == "Alexandra Zena"
    assert profile['risk_score'] >= 40 # ListaHu alert
    assert profile['certainty_score'] >= 90 # Gov source present
    
    print("\n--- TEST PASSED: OmniIdentityResolver v10 is OPERATIONAL ---")

if __name__ == "__main__":
    asyncio.run(test_v10_resolver())
