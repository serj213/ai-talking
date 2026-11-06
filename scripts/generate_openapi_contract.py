import json
from pathlib import Path

project_root = Path(__file__).parent.parent
source_path = project_root / "openapi" / "openapi.yaml"
target_path = project_root / "src" / "talking_agent" / "transport" / "http" / "generated_contract.py"


def main() -> None:
    contract = json.loads(source_path.read_text())
    health_path = next(iter(contract["paths"]))
    health_status_code = next(iter(contract["paths"][health_path]["get"]["responses"]))
    status_value = contract["components"]["schemas"]["HealthResponse"]["properties"]["status"]["const"]

    target_path.write_text(
        "from typing import Literal\n\n"
        "from pydantic import BaseModel, ConfigDict\n\n"
        f'HEALTH_PATH = "{health_path}"\n\n'
        f"HEALTH_STATUS_CODE = {health_status_code}\n\n"
        "class HealthResponse(BaseModel):\n"
        "    model_config = ConfigDict(extra=\"forbid\")\n\n"
        f"    status: Literal[\"{status_value}\"]\n"
    )


if __name__ == "__main__":
    main()
