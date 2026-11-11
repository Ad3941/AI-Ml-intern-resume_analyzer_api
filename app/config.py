import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    DEFAULT_MODEL: str = "openai/gpt-oss-20b"  # Added the required 'openai/' prefix
    MAX_TOKENS: int = 1500
    TEMPERATURE: float = 0.3

settings = Settings()

# import os
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()

# # Initialize the OpenAI client pointing to Groq's base URL
# client = OpenAI(
#     api_key=os.getenv("GROQ_API_KEY"),
#     base_url="https://api.groq.com/openai/v1",
# )

# # Use a universally available Groq model
# response = client.chat.completions.create(
#     model="llama-3.3-70b-versatile",  # Replaced gpt-oss-20b with a supported model
#     messages=[
#         {"role": "user", "content": "Explain the importance of fast language models"}
#     ],
#     temperature=0.3,
#     max_tokens=1500
# )

# print(response.choices[0].message.content)