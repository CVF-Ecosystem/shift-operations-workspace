from __future__ import annotations
from typing import Any, Protocol
from pydantic import BaseModel

class ProviderRequest(BaseModel):
    task_type: str
    context: dict[str, Any]
    output_schema: dict[str, Any]
    timeout_seconds: int = 30
    max_output_tokens: int = 2000

class ProviderResult(BaseModel):
    output: dict[str, Any]
    provider_id: str
    model_id: str
    usage: dict[str, int | float] = {}

class AIProvider(Protocol):
    provider_id: str
    async def generate_structured_output(self, request: ProviderRequest) -> ProviderResult: ...
    async def health_check(self) -> dict[str, Any]: ...
    async def cancel_request(self, request_id: str) -> None: ...
