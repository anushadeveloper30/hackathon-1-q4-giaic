import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pathlib

# Load environment variables
load_dotenv()

# --- Configuration ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    print("API Key Loaded Successfully")
    genai.configure(api_key=GOOGLE_API_KEY)
else:
    print("Error: GOOGLE_API_KEY not found. Please set it in your .env file.")
    # Exit or raise error, depending on desired behavior. For now, we'll let it proceed but API calls will fail.

# Initialize Gemini Model
# Using gemini-1.5-flash as it's generally good for chat applications and cost-effective
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    model = None # Set to None so chat endpoint can handle it


# --- RAG Logic: Read Markdown Files ---
def read_book_content(dir_path: str = "docs") -> str:
    combined_content = ""
    base_path = pathlib.Path(dir_path)

    if not base_path.exists():
        print(f"Warning: Directory '{dir_path}' not found. No book content loaded.")
        return combined_content
    
    # Find all .md files recursively
    md_files = list(base_path.glob("**/*.md"))

    if not md_files:
        print(f"Warning: No markdown files found in '{dir_path}'. The agent will have no specific book context.")

    for file_path in md_files:
        try:
            with open(file_path, 'utf-8') as f:
                content = f.read()
                combined_content += f"\n--- FILE: {file_path.name} ---\n{content}\n"
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")

    return combined_content

# Load book content once when the application starts
BOOK_CONTEXT = read_book_content()


# --- FastAPI Application ---
app = FastAPI()

# Add CORS middleware to allow requests from your Next.js frontend
# Adjust origins as necessary for your deployment
origins = [
    "http://localhost:3000",  # Default Next.js frontend port
    "http://127.0.0.1:3000",
    # You might add other origins if your frontend is deployed elsewhere
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not GOOGLE_API_KEY or not model:
        raise HTTPException(
            status_code=500,
            detail="Gemini API is not configured. Please check GOOGLE_API_KEY in your .env file."
        )

    user_message = request.message

    # Construct the prompt for Gemini, including the RAG context and the strict instructions
    prompt = f"""You are an AI assistant specialized in Anusha's book content.
Your knowledge is strictly limited to the provided book content.
Always strive to provide comprehensive and relevant answers *solely* based on the provided book content.
If a question is outside the scope of the book content, you MUST respond with "Mera ilm sirf Anusha ki is book tak mehdood hai."
Do not provide any information or opinions not found in the book.

--- START OF BOOK CONTENT ---
{BOOK_CONTEXT if BOOK_CONTEXT else "No book content available."}---
END OF BOOK CONTENT ---

User's question: {user_message}

Your answer:"""

    try:
        response = model.generate_content(prompt)
        # Assuming the response object directly contains the text.
        # This might need adjustment based on the exact structure of `response` from google.generativeai
        ai_reply = response.text
        return {"reply": ai_reply}
    except Exception as e:
        print(f"Error generating content with Gemini: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get response from AI: {e}")

# To run this FastAPI application:
# 1. Save this file as main.py
# 2. Run 'uvicorn main:app --reload --port 8000' in your terminal
