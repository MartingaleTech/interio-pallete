from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Interio Palette API"
    debug: bool = True
    cors_origins: list = ["*"]


settings = Settings()
