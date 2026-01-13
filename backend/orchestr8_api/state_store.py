from __future__ import annotations

import json
import hashlib
import os
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import boto3

from .models import Orchestr8State
from .config import Settings


@runtime_checkable
class StateStore(Protocol):
    def load(self) -> Orchestr8State: ...
    def save(self, state: Orchestr8State) -> None: ...
    def store_patch(self, patch_text: str) -> str: ...


@dataclass
class LocalStateStore:
    settings: Settings

    def load(self) -> Orchestr8State:
        path = self.settings.local_state_path
        try:
            with open(path, "r", encoding="utf-8") as f:
                return Orchestr8State.model_validate_json(f.read())
        except Exception:
            return Orchestr8State()

    def save(self, state: Orchestr8State) -> None:
        path = self.settings.local_state_path
        with open(path, "w", encoding="utf-8") as f:
            f.write(state.model_dump_json(indent=2))

    def store_patch(self, patch_text: str) -> str:
        os.makedirs(self.settings.local_patch_dir, exist_ok=True)
        patch_hash = hashlib.md5(patch_text.encode("utf-8")).hexdigest()
        filename = os.path.join(self.settings.local_patch_dir, f"{patch_hash}.patch")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(patch_text)
        return os.path.abspath(filename)


@dataclass
class S3StateStore:
    settings: Settings
    s3 = boto3.client("s3")

    def _state_key(self) -> str:
        return f"{self.settings.s3_prefix}/state.json"

    def load(self) -> Orchestr8State:
        try:
            obj = self.s3.get_object(Bucket=self.settings.s3_bucket, Key=self._state_key())
            raw = obj["Body"].read().decode("utf-8")
            return Orchestr8State.model_validate_json(raw)
        except Exception:
            return Orchestr8State()

    def save(self, state: Orchestr8State) -> None:
        self.s3.put_object(
            Body=state.model_dump_json(),
            Bucket=self.settings.s3_bucket,
            Key=self._state_key(),
            ContentType="application/json",
        )

    def store_patch(self, patch_text: str) -> str:
        patch_hash = hashlib.md5(patch_text.encode("utf-8")).hexdigest()
        key = f"{self.settings.s3_prefix}/patches/{patch_hash}.patch"
        self.s3.put_object(
            Body=patch_text,
            Bucket=self.settings.s3_bucket,
            Key=key,
            ContentType="text/plain",
        )
        return f"https://{self.settings.s3_bucket}.s3.amazonaws.com/{key}"


def build_state_store(settings: Settings) -> StateStore:
    use_s3 = os.getenv("ORCH_USE_S3", "1") not in {"0", "false", "False"}
    if use_s3:
        return S3StateStore(settings=settings)
    return LocalStateStore(settings=settings)
