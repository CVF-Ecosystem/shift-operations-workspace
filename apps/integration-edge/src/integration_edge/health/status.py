from dataclasses import dataclass


@dataclass(frozen=True)
class EdgeReadiness:
    key_registry: bool
    sql_store: bool
    nonce_rate_store: bool
    quarantine_sink: bool
    core_port: bool
    outbound_port: bool

    @property
    def ready(self) -> bool:
        return all(self.__dict__.values())

    def public(self) -> dict[str, object]:
        return {"status": "ready" if self.ready else "not_ready", "checks": dict(self.__dict__)}
