from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url : str
    secret_key: str
    algorithm : str
    debug: bool = False
    
    class Config:
        env_file = ".env"
    