from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Ontology Engine KG"
    app_env: str = "dev"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    use_neo4j: bool = False

    postgres_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ontology"
    use_postgres: bool = False

    vector_dir: str = ".vectorstore"
    top_k_retrieval: int = 5

    llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = Field(default=None, repr=False)


settings = Settings()
