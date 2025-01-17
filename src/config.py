from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    ID_INSTANCE: str
    API_TOKEN_INSTANCE: str
    REDIS_HOST: str
    REDIS_PORT: int
    API_BASE_URL: str
    API_USERNAME: str
    API_PASSWORD: str

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
