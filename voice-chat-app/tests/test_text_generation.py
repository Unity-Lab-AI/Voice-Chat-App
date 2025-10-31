"""Unit tests for the lightweight PolliLib helper."""

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pollilib import PolliTextGenerator


class PolliLibTextGenerationTests(unittest.TestCase):
    """Verify basic text generation utilities behave as expected."""

    def setUp(self) -> None:
        self.generator = PolliTextGenerator()

    def test_generate_formats_prompt(self) -> None:
        """The generator should embed the prompt inside a deterministic response."""

        prompt = "Hello world"
        expected = "Polli library responds: Hello world."
        self.assertEqual(self.generator.generate(prompt), expected)

    def test_generate_handles_empty_input(self) -> None:
        """Whitespace-only prompts are sanitized and still produce a message."""

        prompt = "   \n\t"
        result = self.generator.generate(prompt)
        self.assertIn("(empty prompt)", result)

    def test_generate_variations_returns_expected_count(self) -> None:
        """The generator should return the requested number of variations."""

        variations = self.generator.generate_variations("Hi there", count=2)
        self.assertEqual(len(variations), 2)
        for index, variation in enumerate(variations, start=1):
            self.assertIn(f"Variation {index}.", variation)

    def test_summarize_concatenates_sentences(self) -> None:
        """The summarizer should concatenate sanitized sentences."""

        summary = self.generator.summarize(["Hello   ", "  world!  "])
        self.assertEqual(summary, "Hello world!")

    def test_generate_variations_rejects_invalid_count(self) -> None:
        """Requesting fewer than one variation should raise a ValueError."""

        with self.assertRaises(ValueError):
            self.generator.generate_variations("Nope", count=0)


if __name__ == "__main__":
    unittest.main()
