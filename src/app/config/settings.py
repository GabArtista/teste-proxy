from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseModel):
    host: str = Field(default="localhost", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    user: str = Field(default="analytics", alias="POSTGRES_USER")
    password: str = Field(default="analytics", alias="POSTGRES_PASSWORD")
    name: str = Field(default="sabores", alias="POSTGRES_DB")

    @property
    def url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.name}"
        )


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()
    app_name: str = "sabores-observability"

    class Config:
        env_nested_delimiter = "__"
        extra = "ignore"


settings = Settings()  # singleton style
