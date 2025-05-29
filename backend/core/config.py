from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SECRET_KEY: str
    FRONTEND_URL: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_PROJECT_ID: str  # Added for clarity in client_config

    @property
    def GOOGLE_SCOPES(self):
        return (
            "openid https://www.googleapis.com/auth/userinfo.email "
            "https://www.googleapis.com/auth/userinfo.profile "
            "https://www.googleapis.com/auth/drive.file"
        )


settings = Settings()

if (
    not settings.GOOGLE_CLIENT_ID
    or not settings.GOOGLE_CLIENT_SECRET
    or not settings.SECRET_KEY
):
    raise ValueError(
        "GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and SECRET_KEY must be set in environment variables or .env file"
    )
