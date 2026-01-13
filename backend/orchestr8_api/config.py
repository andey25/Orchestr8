from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    service_name: str = "Orchestr8"
    github_token_env: str = "GITHUB_API_KEY"

    # State storage
    s3_bucket: str = os.getenv("ORCH_S3_BUCKET", "soham-govande")
    s3_prefix: str = os.getenv("ORCH_S3_PREFIX", "orchestr8")
    local_state_path: str = os.getenv("ORCH_LOCAL_STATE", "./.orchestr8_state.json")
    local_patch_dir: str = os.getenv("ORCH_LOCAL_PATCH_DIR", "./.orchestr8_patches")

    # OpenAI
    openai_model: str = os.getenv("ORCH_OPENAI_MODEL", "gpt-4o-mini")
    openai_temperature: float = float(os.getenv("ORCH_OPENAI_TEMPERATURE", "0"))

    # GitHub fork
    fork_owner: str = os.getenv("ORCH_FORK_OWNER", "")
    enable_forking: bool = os.getenv("ORCH_ENABLE_FORKING", "1") not in {"0", "false", "False"}

    # CORS
    cors_allow_origins: list[str] = os.getenv("ORCH_CORS_ORIGINS", "*").split(",")


def get_settings() -> Settings:
    return Settings()
