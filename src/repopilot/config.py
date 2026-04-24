from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore",
    )

    openai_api_key: str = ""
    openai_base_url: str = "https://api.timebackward.com/v1"
    openai_model: str = "gpt-5.3"
    openai_embedding_model: str = "text-embedding-3-small"

    github_token: str = ""

    repopilot_db_path: str
    repopilot_chroma_path: str

settings = Settings()
