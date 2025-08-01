from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',env_ignore_empty=True, extra='ignore'
    )
    POSTGRES_DB:str
    SECRET_KEY:str
    ALGORITHM:str

settings = Settings()