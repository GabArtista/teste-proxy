from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_user: str = "analytics"
    postgres_password: str = "analytics"
    postgres_db: str = "sabores"
    app_name: str = "sabores-observability"

    def db_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    class Config:
        env_prefix = ""
        case_sensitive = False


settings = Settings()  # singleton style
