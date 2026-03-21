from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class AIProcessor:
    """
    Service to process OSINT data using the new Google GenAI SDK.
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    async def generate_semantic_summary(self, profile: dict, news: list = None) -> str:
        if not self.client:
            return "AI Analysis unavailable (Check API Key)"
            
        news_context = "\n".join([f"- {n.get('title')}: {n.get('snippet')}" for n in news]) if news else "No se encontraron noticias recientes."
        
        prompt = f"""
        Genera un Dossier Ejecutivo de 2 párrafos sobre:
        Sujeto: {profile.get('identity', {}).get('full_name', 'Desconocido')}
        Riesgo: {profile.get('risk_score', 0)}
        Certeza: {profile.get('certainty_score', 0)}
        Noticias:
        {news_context}
        
        Responde en español profesional.
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"Error AI: {str(e)}"

    async def summarize_person(self, name: str, data: dict) -> str:
        # Compatibility wrapper
        return await self.generate_semantic_summary(data)
