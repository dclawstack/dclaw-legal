from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8099
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_legal"
    redis_url: str = "redis://localhost:6379/0"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    openrouter_api_key: str = ""
    cors_origins: str = "http://localhost:3013,http://localhost:3000"

    docusign_base_url: str = "https://demo.docusign.net/restapi"
    docusign_account_id: str = ""
    docusign_access_token: str = ""
    docusign_webhook_secret: str = ""


settings = Settings()
