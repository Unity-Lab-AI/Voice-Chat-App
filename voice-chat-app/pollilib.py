"""A minimal text generation helper used for CI smoke tests."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class PolliTextGenerator:
    """Simple, deterministic text generator.

    The implementation is intentionally lightweight so it can be executed during
    CI without external dependencies. It offers a tiny surface area that mimics
    what a real text generation helper could provide.
    """

    prefix: str = "Polli"
    suffix: str = "library"

    def generate(self, prompt: str) -> str:
        """Generate a formatted response from the provided prompt.

        The response is deterministic, making it predictable for testing while
        still resembling a text-generation workflow.
        """

        sanitized = prompt.strip()
        if not sanitized:
            sanitized = "(empty prompt)"
        return f"{self.prefix} {self.suffix} responds: {sanitized}."

    def generate_variations(self, prompt: str, count: int = 3) -> List[str]:
        """Return several variations derived from the prompt."""

        if count < 1:
            raise ValueError("count must be at least 1")
        base = self.generate(prompt)
        return [f"{base} Variation {index + 1}." for index in range(count)]

    def summarize(self, sentences: Iterable[str]) -> str:
        """Summarize the provided sentences into a single string."""

        sanitized = [sentence.strip() for sentence in sentences if sentence.strip()]
        if not sanitized:
            return f"{self.prefix} {self.suffix} has nothing to summarize."
        return " ".join(sanitized)
