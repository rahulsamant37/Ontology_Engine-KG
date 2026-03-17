from __future__ import annotations

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Ontology Engine KG"
    app_env: str = "dev"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = Field(
        default="neo4j",
        validation_alias=AliasChoices("NEO4J_USER", "NEO4J_USERNAME"),
    )
    neo4j_password: str = "password"
    use_neo4j: bool | None = None

    postgres_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ontology"
    use_postgres: bool = False

    vector_dir: str = ".vectorstore"
    top_k_retrieval: int = 5

    llm_model: str = "gpt-4o-mini"
    openai_api_key: str | None = Field(default=None, repr=False)

    @model_validator(mode="after")
    def _derive_use_neo4j(self) -> "Settings":
        if self.use_neo4j is None:
            self.use_neo4j = any(
                [
                    self.neo4j_uri != "bolt://localhost:7687",
                    self.neo4j_user != "neo4j",
                    self.neo4j_password != "password",
                ]
            )
        return self


settings = Settings()
