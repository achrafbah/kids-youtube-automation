"""Base agent class for the Kids YouTube Production Studio."""

import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from google import genai

# Fix Windows console encoding for Arabic characters
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

class BaseAgent(ABC):
    """Abstract base class for all studio department agents."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = self.base_dir / "data"
        self.characters_dir = self.base_dir / "characters"
        self.scenes_dir = self.characters_dir / "scenes"
        self.output_dir = self.base_dir / "output"
        self.env_file = self.base_dir / ".env"
        self._client = None

    def get_api_key(self) -> str:
        """Retrieve Gemini API key from .env or environment variable."""
        if self.env_file.exists():
            for line in open(self.env_file, encoding="utf-8"):
                if line.startswith("GEMINI_API_KEY="):
                    return line.strip().split("=", 1)[1]
        return os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6Ly6CghBsKIp9KFboAoEWe_N7hlrKwYhzBosimjI_JVrA")

    @property
    def client(self) -> genai.Client:
        """Lazy-loaded Google GenAI SDK client."""
        if self._client is None:
            self._client = genai.Client(api_key=self.get_api_key())
        return self._client

    def log(self, message: str):
        """Standardized studio log format."""
        print(f"[{self.name} | {self.role}] {message}", flush=True)

    @abstractmethod
    def run(self, *args, **kwargs):
        """Execute agent workflow."""
        pass
