from fastapi import FastAPI, UploadFile, File, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from app.services import ResumeAnalysisService
from app.schemas import AnalysisResponse
import logging

# Imports for rate limiting via slowapi
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Limiter using client IP address
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AI Utility API - Resume Summarizer & Text Analyzer",
    version="1.0.0",
    description="Cost-optimized and low-latency utility API built with FastAPI and Groq."
)

# Bind the limiter to the FastAPI app state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the AI Utility API - Resume Summarizer & Text Analyzer",
        "docs_url": "/docs",
        "health_check": "/health"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "resume-analyzer-api"}

@app.post("/api/v1/analyze-resume", response_model=AnalysisResponse)
@limiter.limit("5/minute")  # Limits this endpoint to 5 requests per minute per IP
async def analyze_resume_json(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files are supported."
        )
    
    try:
        contents = await file.read()
        extracted_text = ResumeAnalysisService.extract_text_from_pdf(contents)
        
        if not extracted_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Could not extract text from the provided PDF."
            )
            
        analysis_result = ResumeAnalysisService.analyze_text_sync(extracted_text)
        return analysis_result
        
    except Exception as e:
        logger.error(f"Error processing resume analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during LLM processing: {str(e)}"
        )

@app.post("/api/v1/stream-resume")
@limiter.limit("5/minute")  # Limits streaming endpoint as well
async def analyze_resume_streaming(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files are supported."
        )
        
    contents = await file.read()
    extracted_text = ResumeAnalysisService.extract_text_from_pdf(contents)
    
    if not extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract text from the provided PDF."
        )

    return StreamingResponse(
        ResumeAnalysisService.analyze_text_stream(extracted_text),
        media_type="text/event-stream"
    )