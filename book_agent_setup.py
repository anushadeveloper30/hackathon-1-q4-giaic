import os
from dotenv import load_dotenv, find_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from typing import Any
import glob # For finding files
import pathlib # For path manipulation and reading files

# Load environment variables from .env file
_: bool = load_dotenv(find_dotenv())

# ONLY FOR TRACING - not directly used by Gemini, but good practice if using OpenAI for other agents
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")

gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

# 1. Which LLM Service?
# Configure AsyncOpenAI to use the Gemini API endpoint
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 2. Which LLM Model?
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash", # Using gemini-1.5-flash as per original request
    openai_client=external_client
)

# Function to recursively read all markdown files from a directory
def read_book_content(dir_path: str) -> str:
    combined_content = ""
    # Use pathlib for more robust path handling
    base_path = pathlib.Path(dir_path)
    
    # Find all .md files recursively
    md_files = glob.glob(str(base_path / "**/*.md"), recursive=True)

    for file_path_str in md_files:
        try:
            with open(file_path_str, 'utf-8') as f:
                content = f.read()
                combined_content += f"\n--- FILE: {file_path_str} ---\n{content}\n"
        except Exception as e:
            print(f"Error reading file {file_path_str}: {e}")
            
    return combined_content

# Get the book content
book_content: str = read_book_content('docs')

# Define the Book Agent
book_agent: Agent = Agent(
    name="AnushaBookAgent",
    instructions=f"""You are an AI assistant specialized in Anusha's book content.
Your knowledge is strictly limited to the provided book content.
Always strive to provide comprehensive and relevant answers *solely* based on the provided book content.
If a question is outside the scope of the book content, you MUST respond with "Mera ilm sirf Anusha ki is book tak mehdood hai."
Do not provide any information or opinions not found in the book.

--- START OF BOOK CONTENT ---
{book_content}
--- END OF BOOK CONTENT ---

""",
    model=llm_model,
    # No guardrails for now, as per the simplification plan.
    # If specific input/output filtering is needed beyond prompt engineering,
    # guardrails can be added here.
)

# Test run for the Book Agent
if __name__ == "__main__":
    print("Initializing Anusha's Book Agent...")
    print("Book content loaded. Agent ready.")

    while True:
        user_query = input("\nAsk Anusha's Book Agent (type 'exit' to quit): ")
        if user_query.lower() == 'exit':
            break

        if not gemini_api_key:
            print("Error: GEMINI_API_KEY is not set. Please set it in your .env file.")
            continue

        try:
            # The 'agents' library expects messages in a specific format
            res = Runner.run_sync(book_agent, [{"role": "user", "content": user_query}])
            
            # The final_output will contain the generated text from the model
            # For chat models, it's usually res.final_output
            # If the response format is different, this might need adjustment.
            print(f"\nAnusha's Book Agent: {res.final_output}")
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Please ensure your GEMINI_API_KEY is correct and the API endpoint is reachable.")

