from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Face Attendance API"
    database_url: str
    face_match_threshold: float = 0.5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()