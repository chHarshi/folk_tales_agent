import config

def get_llm(provider="gemini", temperature=0.4):
    if provider == "ollama":
        from langchain_ollama import ChatOllama
        import os
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(model=config.OLLAMA_MODEL, temperature=temperature, base_url=base_url)
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(model=config.LLM_MODEL, temperature=temperature)