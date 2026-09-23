import json
import urllib.request
import urllib.error
from typing import Dict, Any

# Using a local Ollama instance (ollama.com does not host a public API endpoint)
OLLAMA_API_KEY = "" # Not needed for local Ollama
OLLAMA_CLOUD_URL = "http://localhost:11434/api/generate"
# The user wants to use Qwen3 based on their previous prompt, or Phi/Llama. We'll set Qwen as the default.
DEFAULT_MODEL = "qwen2.5" 

def evaluate_with_llm(resume_text: str, jd_text: str, model_name: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Calls the Ollama Cloud API to perform a deep semantic analysis of the resume against the JD.
    Returns a dictionary containing a 'score' (0-100) and 'reasoning'.
    """
    prompt = f"""You are an expert ATS (Applicant Tracking System) and technical recruiter.
Your task is to deeply analyze a candidate's resume against a job description.
Do not evaluate formatting or keyword density; evaluate the true semantic alignment of the candidate's achievements and skills against the core responsibilities and requirements of the role.

Return ONLY a valid JSON object in the following format, with no markdown formatting or extra text:
{{
    "score": <an integer between 0 and 100 representing the match quality>,
    "reasoning": "<a 2-3 sentence explanation of why this score was given>"
}}

Job Description:
{jd_text}

Candidate Resume:
{resume_text}
"""

    data = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1
        }
    }

    try:
        req = urllib.request.Request(
            OLLAMA_CLOUD_URL, 
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {OLLAMA_API_KEY}'
            }
        )
        
        with urllib.request.urlopen(req, timeout=45) as response:
            result = json.loads(response.read().decode('utf-8'))
            response_text = result.get("response", "{}").strip()
            
            # The model should return strict JSON due to format="json"
            parsed = json.loads(response_text)
            
            score = parsed.get("score", 60)
            # Ensure score is an integer between 0 and 100
            try:
                score = max(0, min(100, int(score)))
            except:
                score = 60
                
            return {
                "score": score,
                "reasoning": parsed.get("reasoning", "LLM completed analysis.")
            }
            
    except Exception as e:
        print(f"Ollama Cloud API Error: {str(e)}")
        return {
            "score": 65, 
            "reasoning": f"Deep LLM pass failed with the Ollama Cloud API. Error: {str(e)}"
        }
