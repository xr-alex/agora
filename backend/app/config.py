from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    anthropic_api_key: str = ""
    llm_provider: str = "ollama"
    llm_model: str = "llama3.2"
    ollama_base_url: str = "http://localhost:11434"

    class Config:
        env_file = ".env"


settings = Settings()
