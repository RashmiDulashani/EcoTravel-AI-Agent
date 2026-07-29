import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables from .env into os.environ
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


def get_fast_llm() -> ChatOpenAI:
    """
    Returns the fast, cheap Groq model used for routing and reflection.
    temperature=0 for deterministic, consistent classification decisions.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found. Check your .env file.")

    return ChatOpenAI(
        model="llama-3.1-8b-instant",
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        temperature=0,
        max_tokens=1024
    )


def get_reasoning_llm() -> ChatOpenAI:
    """
    Returns the stronger OpenRouter model used for trip planning.
    temperature=0.4 allows some creative variety while staying focused.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not found. Check your .env file.")

    return ChatOpenAI(
        model="anthropic/claude-haiku-4.5",
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1",
        temperature=0.4,
        max_tokens=2048
    )