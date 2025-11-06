from pydantic import BaseModel
import os


class Settings(BaseModel):
    app_name: str = "Interio Palette API"
    debug: bool = True
    cors_origins: list = ["*"]
    testing: bool = os.getenv("TESTING", "false").lower() == "true"


settings = Settings()
