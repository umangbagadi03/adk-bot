from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import asyncio

load_dotenv()

# --- Tool functions ---
def greet(name: str) -> str:
    return f"Hello {name}, welcome to the PDF + ADK Agent!"

import os

def extract_pdf_text(pdf_path: str) -> str:
    try:
        full_path = os.path.abspath(pdf_path)
        print(f"[DEBUG] Attempting to open: {full_path}")
        print(f"[DEBUG] Current working dir: {os.getcwd()}")

        reader = PdfReader(full_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text.strip() if text else "PDF has no extractable text."
    except Exception as e:
        return f"Error reading PDF: {e}"


# --- Agent ---
llm = LiteLlm(model="groq/llama3-8b-8192")

agent = Agent(
    name="pdf_agent",
    model=llm,
    description="Agent that can greet users and read PDF files.",
    instruction="Use the tools to either greet the user or read from a PDF.",
    tools=[greet, extract_pdf_text]
)

APP_NAME="pdf_agent_adk"
USER_ID = "umang"
SESSION_ID = "sess1"

# --- Main ---
async def main():
    print("\n--- Starting Agent ---")
    session_service = InMemorySessionService()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    print("\nGreeting Response:")
    async for message in runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message={"role": "user", "content": "greet:name=Umang"}
    ):
        print(message)

    print("\nPDF Extraction Response:")
    async for message in runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message={
            "role": "user",
            "content": "extract_pdf_text:pdf_path=/Users/umangbagadi/Documents/projects/pdf_agent_adk/apps/sample.pdf"
        }

    ):
        print(message)

if __name__ == "__main__":
    asyncio.run(main())

root_agent = agent