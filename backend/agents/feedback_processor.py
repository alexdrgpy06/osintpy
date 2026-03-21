import os
import asyncio
from typing import List, Dict
from google import genai
from dotenv import load_dotenv
from agents.persistence import ProfilePersistenceAgent

load_dotenv()

class FeedbackProcessor:
    """
    Uses Gemini to analyze user feedback and generate a refinement log
    suggesting code/logic improvements.
    """
    @staticmethod
    async def generate_refinement_report() -> str:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "No API Key found for Gemini."

        # 1. Get all pending feedback
        feedbacks = ProfilePersistenceAgent.get_all_feedback()
        if not feedbacks:
            return "No hay feedback pendiente para procesar."

        # 2. Format feedback for Gemini
        feedback_summary = ""
        for f in feedbacks:
            feedback_summary += f"- Perfil ID: {f['profile_id']} | Campo: {f['field']} | Valor Incorrecto: {f['incorrect_value']} | Sugerencia: {f['correct_value']} | Comentario: {f['comment']}\n"

        # 3. Ask Gemini for a technical improvement plan
        try:
            client = genai.Client(api_key=api_key)
            
            prompt = f"""
            Como Ingeniero de Software Senior y Experto en OSINT, analiza el siguiente feedback de usuarios 
            sobre datos incorrectos en nuestro sistema. Genera un 'Log de Refinamiento Técnico' que identifique:
            
            1. Patrones de errores recurrentes.
            2. Sugerencias de mejora en los scrapers o en la lógica de consolidación.
            3. Acciones correctivas para el código.
            
            FEEDBACK DE USUARIOS:
            {feedback_summary}
            
            Resumen de mejora técnica (en español):
            """
            
            def do_genai():
                return client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt
                )
            
            response = await asyncio.to_thread(do_genai)
            return response.text.strip()
        except Exception as e:
            return f"Error procesando feedback con Gemini: {str(e)}"
