import json
import io
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import settings
from pypdf import PdfReader

client = Groq(api_key=settings.GROQ_API_KEY)

# Define tool schema for function calling
CONTACT_EXTRACTION_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_contact_details",
        "description": "Extract precise candidate contact details from resume text.",
        "parameters": {
            "type": "object",
            "properties": {
                "full_name": {"type": "string", "description": "Candidate's full name"},
                "email": {"type": "string", "description": "Candidate email address"},
                "phone_number": {"type": "string", "description": "Candidate phone number"},
                "linkedin_url": {"type": "string", "description": "Candidate LinkedIn profile URL or handle"}
            },
            "required": ["full_name", "email", "phone_number"]
        }
    }
}

class ResumeAnalysisService:
    @staticmethod
    def extract_text_from_pdf(file_bytes: bytes) -> str:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
    def analyze_text_sync(text: str) -> dict:
        prompt = (
            "Analyze the following resume text. Extract a concise professional summary, "
            "a list of technical/soft skills, estimated years of experience, and top recommended job roles. "
            "Return output strictly in valid JSON format with keys: "
            "'summary', 'key_skills', 'experience_years_estimated', 'recommended_roles'.\n\n"
            f"Resume Text:\n{text[:4000]}"
        )
        
        response = client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS
        )
        
        result_json = json.loads(response.choices[0].message.content)
        
        # Call tool to extract contact details as well
        contact_response = client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=[{"role": "user", "content": f"Extract contact info from this resume:\n{text[:2000]}"}],
            tools=[CONTACT_EXTRACTION_TOOL],
            tool_choice={"type": "function", "function": {"name": "extract_contact_details"}}
        )
        
        tool_call = contact_response.choices[0].message.tool_calls
        if tool_call:
            args = json.loads(tool_call[0].function.arguments)
            result_json["contact_details"] = args
        else:
            result_json["contact_details"] = {}
            
        return result_json

    @staticmethod
    async def analyze_text_stream(text: str):
        prompt = (
            "Analyze the following resume text and stream back a structured professional summary, "
            "key skills, estimated experience, and recommended roles in markdown format.\n\n"
            f"Resume Text:\n{text[:4000]}"
        )
        
        stream = client.chat.completions.create(
            model=settings.DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            stream=True
        )
        
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta