from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

    jwt_secret_key: str
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    email_verification_expire_minutes: int = 20

    smtp_host: str
    smtp_port: int = 587
    smtp_username: str
    smtp_password: SecretStr
    smtp_from: str

settings = Settings()