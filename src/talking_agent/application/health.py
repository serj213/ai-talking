from typing import Literal


class HealthService:
    def status(self) -> Literal["ok"]:
        return "ok"
