from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    email_dir: str = "emails"
    embed_model: str = "multi-qa-MiniLM-L6-cos-v1"
    openai_api_key: str
    login_username: str
    login_password: str
    secret_key: str
    gmail_username: str
    gmail_password: str

    class Config:
        env_file = ".env"


settings = Settings()
