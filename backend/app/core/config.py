from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    
    DISCORD_BOT_TOKEN: str
    DISCORD_CHANNEL_ID: str
    
    SECRET_TOKEN: str
    
    class Config:
        env_file = ".env"