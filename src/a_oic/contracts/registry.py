from typing import Dict, Set

SUPPORTED_VERSIONS: Set[str] = {"1.0"}

LATEST_VERSION = "1.0"


def is_supported(version: str) -> bool:
    return version in SUPPORTED_VERSIONS
