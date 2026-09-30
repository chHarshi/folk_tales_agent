import config

def get_llm(provider="gemini", temperature=0.4):
    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(model=config.OLLAMA_MODEL, temperature=temperature)
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(model=config.LLM_MODEL, temperature=temperature)