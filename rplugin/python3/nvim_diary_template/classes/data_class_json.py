# pylint: disable=all
import json
from typing import Any

import dataclasses


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)

        return super().default(o)
