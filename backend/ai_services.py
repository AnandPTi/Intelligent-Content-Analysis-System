import google.generativeai as genai
from typing import Dict, List
import json
import asyncio

class AIService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-pro")
        self.embedding_model = "models/text-embedding-004"

    async def analyze_content(self, text: str) -> Dict:
        prompt = """
        Analyze the following educational content and provide:
        1. Complexity level (1-5)
        2. Key concepts (max 5)
        3. Prerequisites
        4. Learning objectives
        5. Readability metrics

        Content: {text}

        Provide the analysis in JSON format, nothing extra just a JSON Format text because I have to use it for further request and storing i only JSON format, don't even include ```json in beginning.
        """
        
        # Convert to synchronous call since Gemini API doesn't support native async
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.model.generate_content(prompt.format(text=text))
        )
        
        # Parse the response text as JSON
        try:
            # Assuming the response is already in JSON format
            raw_text = response.candidates[0].content.parts[0].text
            #print("Content Text:", content_text)  # Log content text for debugging
            if raw_text.startswith("```json") and raw_text.endswith("```"):
                raw_text = raw_text[7:-3].strip()

            # Parse the cleaned-up JSON
            analysis = json.loads(raw_text)
            # analysis = json.loads(response.text)
        except json.JSONDecodeError:
            # If not in JSON format, create a structured response
            analysis = {
                "complexity_level": 3,
                "key_concepts": ["Not available"],
                "prerequisites": ["Not available"],
                "learning_objectives": ["Not available"],
                "readability_metrics": {
                    "score": "Not available"
                }
            }
            
        return analysis

    async def generate_embeddings(self, text: str) -> List[float]:
        # Convert to synchronous call
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: genai.embed_content(
                model=self.embedding_model,
                content=text
            )
        )
        
        # Extract embeddings from result
        return result['embedding']
