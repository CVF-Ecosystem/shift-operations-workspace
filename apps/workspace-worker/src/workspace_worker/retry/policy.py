from dataclasses import dataclass
@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3
    initial_delay_seconds: int = 5
    backoff_multiplier: float = 2.0
