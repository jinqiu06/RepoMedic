import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from functools import lru_cache

@lru_cache(maxsize = 1)
def get_load() -> ChatOpenAI:
    env_path = Path(__file__).resolve().parent / ".env"

    load_dotenv(env_path)

    api_key = os.getenv('LLM_API_KEY')
    model = os.getenv("LLM_MODEL_ID")
    base_url = os.getenv('LLM_BASE_URL')

    if not api_key:
      raise RuntimeError("缺少 LLM_API_KEY")

    if not model:
      raise RuntimeError("缺少 LLM_MODEL_ID")

    if not base_url:
      raise RuntimeError("缺少 LLM_BASE_URL")
    return ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url=base_url,
        temperature=0,
        timeout=30,
        max_retries=1
    )