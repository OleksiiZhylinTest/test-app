from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

try:
    __version__ = version("ai-adoption-manager")
except PackageNotFoundError:
    try:
        _toml = Path(__file__).parent.parent / "pyproject.toml"
        with open(_toml, encoding="utf-8") as fp:
            for line in fp:
                if line.strip().startswith("version"):
                    __version__ = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
            else:
                __version__ = "0.0.0+unknown"
    except FileNotFoundError:
        __version__ = "0.0.0+unknown"
