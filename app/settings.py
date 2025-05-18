from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    DEBUG: bool = Field(False, env="DEBUG")
    ALLOWED_HOSTS: str = Field("*", env="ALLOWED_HOSTS")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    REDIS_URL: str | None = Field(None, env="REDIS_URL")
    EMAIL_HOST: str | None = Field(None, env="EMAIL_HOST")
    EMAIL_PORT: int = Field(587, env="EMAIL_PORT")
    EMAIL_USER: str | None = Field(None, env="EMAIL_USER")
    EMAIL_PASSWORD: str | None = Field(None, env="EMAIL_PASSWORD")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    CLOUDINARY_CLOUD_NAME: str = Field(..., env="CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY: str = Field(..., env="CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET: str = Field(..., env="CLOUDINARY_API_SECRET")
    GENAI_API_KEY: str = Field(..., env="GENAI_API_KEY")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
